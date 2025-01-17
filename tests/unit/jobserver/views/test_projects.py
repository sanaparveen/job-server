import pytest
import requests
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.utils import timezone

from jobserver.authorization import CoreDeveloper
from jobserver.models import Snapshot
from jobserver.utils import set_from_qs
from jobserver.views.projects import ProjectDetail

from ....factories import (
    OrgFactory,
    ProjectFactory,
    RepoFactory,
    SnapshotFactory,
    UserFactory,
    WorkspaceFactory,
)
from ....fakes import FakeGitHubAPI
from ....utils import minutes_ago


@pytest.mark.parametrize("user", [UserFactory, AnonymousUser])
def test_projectdetail_success(rf, user):
    org = OrgFactory()
    project = ProjectFactory(org=org)
    repo = RepoFactory(url="https://github.com/opensafely/some-research")
    WorkspaceFactory.create_batch(3, project=project, repo=repo)

    request = rf.get("/")

    # instantiate here because pytest-django disables db access by default and
    # our global fixture to re-enable it doesn't trigger early enough for the
    # parametrize call
    request.user = user()

    response = ProjectDetail.as_view(get_github_api=FakeGitHubAPI)(
        request, org_slug=org.slug, project_slug=project.slug
    )

    assert response.status_code == 200

    assert len(response.context_data["repos"]) == 1
    assert response.context_data["repos"] == [
        {
            "name": "some-research",
            "url": "https://github.com/opensafely/some-research",
            "is_private": True,
        }
    ]

    # check the staff-only edit link doesn't show for normal users
    assert "Edit" not in response.context_data


def test_projectdetail_with_multiple_releases(rf, freezer):
    project = ProjectFactory()

    now = timezone.now()

    workspace1 = WorkspaceFactory(project=project)
    snapshot1 = SnapshotFactory(workspace=workspace1, published_at=minutes_ago(now, 2))
    snapshot2 = SnapshotFactory(workspace=workspace1, published_at=minutes_ago(now, 3))

    workspace2 = WorkspaceFactory(project=project)
    snapshot3 = SnapshotFactory(workspace=workspace2, published_at=minutes_ago(now, 1))

    # unpublished
    workspace3 = WorkspaceFactory(project=project)
    snapshot4 = SnapshotFactory(workspace=workspace3, published_at=None)

    workspace4 = WorkspaceFactory(project=project)
    snapshot5 = SnapshotFactory(workspace=workspace4, published_at=minutes_ago(now, 4))

    request = rf.get("/")
    # FIXME: remove this role when releases is deployed to all users
    request.user = UserFactory(roles=[CoreDeveloper])

    response = ProjectDetail.as_view(get_github_api=FakeGitHubAPI)(
        request, org_slug=project.org.slug, project_slug=project.slug
    )

    assert response.status_code == 200

    assert "Outputs" in response.rendered_content

    # check the ordering of responses, should be latest first
    assert len(response.context_data["outputs"]) == 3
    output_pks = list(response.context_data["outputs"].values_list("pk", flat=True))
    expected_pks = [snapshot3.pk, snapshot1.pk, snapshot5.pk]
    assert output_pks == expected_pks

    # check unpublished or published-but-older snapshots are not in the
    # snapshots picked to display for outputs
    snapshots = set_from_qs(Snapshot.objects.all())
    assert snapshot2 not in snapshots
    assert snapshot4 not in snapshots


def test_projectdetail_with_no_github(rf):
    project = ProjectFactory()
    WorkspaceFactory(project=project)

    request = rf.get("/")
    request.user = UserFactory()

    class BrokenGitHubAPI:
        def get_repo_is_private(self, *args):
            raise requests.HTTPError

    response = ProjectDetail.as_view(get_github_api=BrokenGitHubAPI)(
        request, org_slug=project.org.slug, project_slug=project.slug
    )

    assert response.status_code == 200

    # check there is no public/private badge when GitHub returns an
    # unsuccessful response
    assert response.context_data["repos"][0]["is_private"] is None
    assert "Private" not in response.rendered_content
    assert "Public" not in response.rendered_content


def test_projectdetail_with_no_releases(rf):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = UserFactory()

    response = ProjectDetail.as_view(get_github_api=FakeGitHubAPI)(
        request, org_slug=project.org.slug, project_slug=project.slug
    )

    assert response.status_code == 200

    assert len(response.context_data["outputs"]) == 0
    assert "Outputs" not in response.rendered_content


def test_projectdetail_unknown_org(rf):
    project = ProjectFactory()

    request = rf.get("/")
    request.user = UserFactory()

    with pytest.raises(Http404):
        ProjectDetail.as_view()(request, org_slug="test", project_slug=project.slug)


def test_projectdetail_unknown_project(rf):
    org = OrgFactory()

    request = rf.get("/")
    request.user = UserFactory()

    with pytest.raises(Http404):
        ProjectDetail.as_view()(request, org_slug=org.slug, project_slug="test")
