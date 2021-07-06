from datetime import timedelta

import pytest
from django.http import Http404
from django.utils import timezone

from jobserver.views.releases import (
    ProjectReleaseList,
    ReleaseDetail,
    WorkspaceReleaseList,
)

from ...factories import OrgFactory, ProjectFactory, ReleaseFactory, WorkspaceFactory


@pytest.mark.django_db
def test_projectreleaselist_success(rf):
    project = ProjectFactory()
    workspace1 = WorkspaceFactory(project=project)
    workspace2 = WorkspaceFactory(project=project)

    ReleaseFactory(workspace=workspace1, files=["test1", "test2"])
    ReleaseFactory(workspace=workspace2, files=["test3", "test4"])

    request = rf.get("/")

    response = ProjectReleaseList.as_view()(
        request,
        org_slug=project.org.slug,
        project_slug=project.slug,
    )

    assert response.status_code == 200

    assert response.context_data["project"] == project
    assert len(response.context_data["object_list"]) == 2


@pytest.mark.django_db
def test_projectreleaselist_unknown_workspace(rf):
    org = OrgFactory()

    request = rf.get("/")

    with pytest.raises(Http404):
        ProjectReleaseList.as_view()(
            request,
            org_slug=org.slug,
            project_slug="",
        )


@pytest.mark.django_db
def test_releasedetail_no_path_success(rf):
    release = ReleaseFactory()

    request = rf.get("/")

    response = ReleaseDetail.as_view()(
        request,
        org_slug=release.workspace.project.org.slug,
        project_slug=release.workspace.project.slug,
        workspace_slug=release.workspace.name,
        pk=release.id,
        path="",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_releasedetail_unknown_release(rf):
    workspace = WorkspaceFactory()

    request = rf.get("/")
    with pytest.raises(Http404):
        ReleaseDetail.as_view()(
            request,
            org_slug=workspace.project.org.slug,
            project_slug=workspace.project.slug,
            workspace_slug=workspace.name,
            pk="",
        )


@pytest.mark.django_db
def test_releasedetail_with_path_success(rf):
    release = ReleaseFactory()

    request = rf.get("/")

    response = ReleaseDetail.as_view()(
        request,
        org_slug=release.workspace.project.org.slug,
        project_slug=release.workspace.project.slug,
        workspace_slug=release.workspace.name,
        pk=release.id,
        path="test123/some/path",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_workspacereleaselist_success(rf):
    workspace = WorkspaceFactory()
    release1 = ReleaseFactory(
        workspace=workspace,
        files=["test1", "test2"],
        created_at=timezone.now() - timedelta(minutes=3),
    )
    release2 = ReleaseFactory(
        workspace=workspace,
        files=["test2", "test3"],
        created_at=timezone.now() - timedelta(minutes=2),
    )
    release3 = ReleaseFactory(
        workspace=workspace,
        files=["test3", "test4"],
        created_at=timezone.now() - timedelta(minutes=1),
    )

    request = rf.get("/")

    response = WorkspaceReleaseList.as_view()(
        request,
        org_slug=workspace.project.org.slug,
        project_slug=workspace.project.slug,
        workspace_slug=workspace.name,
    )

    assert response.status_code == 200

    assert response.context_data["workspace"] == workspace

    assert response.context_data["files"][0].name == "test1"
    assert response.context_data["files"][0].release == release1
    assert response.context_data["files"][1].name == "test2"
    assert response.context_data["files"][1].release == release2
    assert response.context_data["files"][2].name == "test3"
    assert response.context_data["files"][2].release == release3
    assert response.context_data["files"][3].name == "test4"
    assert response.context_data["files"][3].release == release3


@pytest.mark.django_db
def test_workspacereleaselist_unknown_workspace(rf):
    project = ProjectFactory()

    request = rf.get("/")

    with pytest.raises(Http404):
        WorkspaceReleaseList.as_view()(
            request,
            org_slug=project.org.slug,
            project_slug=project.slug,
            workspace_slug="",
        )
