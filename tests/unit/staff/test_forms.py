from jobserver.models import Backend, User
from jobserver.utils import set_from_qs
from staff.forms import (
    ApplicationApproveForm,
    ProjectEditForm,
    ProjectFeatureFlagsForm,
    ProjectLinkApplicationForm,
    UserForm,
)

from ...factories import ApplicationFactory, BackendFactory, OrgFactory, ProjectFactory


def test_applicationapproveform_success():
    org = OrgFactory(slug="test-org")

    form = ApplicationApproveForm(
        {
            "project_name": "test project",
            "project_number": "42",
            "org": str(org.pk),
        }
    )

    assert form.is_valid(), form.errors


def test_applicationapproveform_with_duplicate_project_name():
    org = OrgFactory()
    project = ProjectFactory()

    form = ApplicationApproveForm(
        {
            "project_name": project.name,
            "project_number": "42",
            "org": str(org.pk),
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "project_name": [f'Project "{project.name}" already exists.']
    }


def test_applicationapproveform_with_duplicate_project_number():
    org = OrgFactory()
    project = ProjectFactory(number=42)

    form = ApplicationApproveForm(
        {
            "project_name": "test",
            "project_number": "42",
            "org": str(org.pk),
        }
    )

    assert not form.is_valid()
    assert form.errors == {
        "project_number": [f'Project with number "{project.number}" already exists.']
    }


def test_projecteditform_number_is_not_required():
    """
    Ensure Project.number isn't required by ProjectEditForm

    Project.number is nullable while we get all project data ported into this
    project.
    """
    org = OrgFactory()
    users = User.objects.all()

    data = {
        "name": "Test",
        "slug": "test",
        "org": str(org.pk),
    }

    form = ProjectEditForm(data=data, users=users)
    assert form.is_valid(), form.errors

    form = ProjectEditForm(data=data | {"number": 123}, users=users)
    assert form.is_valid(), form.errors


def test_projectfeatureflagsform_with_unknown_value():
    form = ProjectFeatureFlagsForm({"flip_to": "test"})

    assert not form.is_valid()

    expected = {
        "flip_to": ["Select a valid choice. test is not one of the available choices."]
    }
    assert form.errors == expected


def test_projectlinkapplicationform_success():
    application = ApplicationFactory(project=None)

    form = ProjectLinkApplicationForm(
        data={"application": application.pk}, instance=None
    )
    assert form.is_valid(), form.errors

    assert form.cleaned_data["application"] == application


def test_projectlinkapplicationform_with_already_linked_application():
    application = ApplicationFactory(project=ProjectFactory())

    form = ProjectLinkApplicationForm(
        data={"application": application.pk}, instance=None
    )

    assert not form.is_valid()

    assert form.errors == {
        "application": ["Can't link Application to multiple Projects"]
    }


def test_projectlinkapplicationform_with_unknown_application():
    form = ProjectLinkApplicationForm(data={"application": "0"}, instance=None)

    assert not form.is_valid()

    assert form.errors == {"application": ["Unknown Application"]}


def test_userform_success():
    backend1 = BackendFactory()
    backend2 = BackendFactory()
    BackendFactory()

    data = {
        "backends": [backend1.slug, backend2.slug],
        "roles": [],
    }
    form = UserForm(
        available_backends=Backend.objects.all(),
        available_roles=[],
        data=data,
    )

    assert form.is_valid(), form.errors

    assert set_from_qs(form.cleaned_data["backends"]) == {backend1.pk, backend2.pk}


def test_userform_with_no_backends():
    available_backends = Backend.objects.filter(slug__in=["tpp"])

    data = {
        "backends": [],
        "roles": [],
    }

    form = UserForm(
        available_backends=available_backends,
        available_roles=[],
        data=data,
    )

    assert form.is_valid()
    assert len(form.cleaned_data["backends"]) == 0


def test_userform_with_unknown_backend():
    BackendFactory.create_batch(5)

    available_backends = Backend.objects.exclude(slug="unknown")

    data = {
        "backends": ["unknown"],
        "roles": [],
    }

    form = UserForm(
        available_backends=available_backends,
        available_roles=[],
        data=data,
    )

    assert not form.is_valid()
    assert form.errors == {
        "backends": [
            "Select a valid choice. unknown is not one of the available choices."
        ]
    }
