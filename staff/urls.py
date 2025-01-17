from django.urls import include, path

from .views.applications import (
    ApplicationApprove,
    ApplicationDetail,
    ApplicationEdit,
    ApplicationList,
    ApplicationRemove,
    ApplicationRestore,
    application_add_org,
)
from .views.backends import (
    BackendCreate,
    BackendDetail,
    BackendEdit,
    BackendList,
    BackendRotateToken,
)
from .views.dashboards import DashboardIndex
from .views.index import Index
from .views.orgs import (
    OrgCreate,
    OrgDetail,
    OrgEdit,
    OrgList,
    OrgProjectCreate,
    OrgRemoveGitHubOrg,
    OrgRemoveMember,
    org_add_github_org,
)
from .views.projects import (
    ProjectAddMember,
    ProjectCreate,
    ProjectDetail,
    ProjectEdit,
    ProjectFeatureFlags,
    ProjectLinkApplication,
    ProjectList,
    ProjectMembershipEdit,
    ProjectMembershipRemove,
)
from .views.redirects import RedirectDelete, RedirectDetail, RedirectList
from .views.repos import (
    PrivateReposDashboard,
    RepoDetail,
    RepoFeatureFlags,
    RepoList,
    RepoSignOff,
)
from .views.researchers import ResearcherEdit
from .views.users import UserDetail, UserList, UserSetOrgs
from .views.workspaces import WorkspaceDetail, WorkspaceEdit, WorkspaceList


app_name = "staff"

application_urls = [
    path("", ApplicationList.as_view(), name="application-list"),
    path("<str:pk_hash>/", ApplicationDetail.as_view(), name="application-detail"),
    path(
        "<str:pk_hash>/approve/",
        ApplicationApprove.as_view(),
        name="application-approve",
    ),
    path(
        "<str:pk_hash>/approve/add-org/",
        application_add_org,
        name="application-add-org",
    ),
    path("<str:pk_hash>/edit/", ApplicationEdit.as_view(), name="application-edit"),
    path(
        "<str:pk_hash>/delete/", ApplicationRemove.as_view(), name="application-delete"
    ),
    path(
        "<str:pk_hash>/restore/",
        ApplicationRestore.as_view(),
        name="application-restore",
    ),
]

backend_urls = [
    path("", BackendList.as_view(), name="backend-list"),
    path("add/", BackendCreate.as_view(), name="backend-create"),
    path("<int:pk>/", BackendDetail.as_view(), name="backend-detail"),
    path("<int:pk>/edit/", BackendEdit.as_view(), name="backend-edit"),
    path(
        "<int:pk>/rotate-token/",
        BackendRotateToken.as_view(),
        name="backend-rotate-token",
    ),
]

dashboard_urls = [
    path("", DashboardIndex.as_view(), name="index"),
    path("repos", PrivateReposDashboard.as_view(), name="repos"),
]

org_urls = [
    path("", OrgList.as_view(), name="org-list"),
    path("add/", OrgCreate.as_view(), name="org-create"),
    path("<slug>/", OrgDetail.as_view(), name="org-detail"),
    path("<slug>/add-github-org/", org_add_github_org, name="org-add-github-org"),
    path("<slug>/add-project/", OrgProjectCreate.as_view(), name="org-project-create"),
    path("<slug>/edit/", OrgEdit.as_view(), name="org-edit"),
    path("<slug>/remove-member/", OrgRemoveMember.as_view(), name="org-remove-member"),
    path(
        "<slug>/remove-github-org/",
        OrgRemoveGitHubOrg.as_view(),
        name="org-remove-github-org",
    ),
]
project_urls = [
    path("", ProjectList.as_view(), name="project-list"),
    path("add/", ProjectCreate.as_view(), name="project-create"),
    path("<slug>/", ProjectDetail.as_view(), name="project-detail"),
    path("<slug>/add-member/", ProjectAddMember.as_view(), name="project-add-member"),
    path("<slug>/edit/", ProjectEdit.as_view(), name="project-edit"),
    path(
        "<slug>/feature-flags/",
        ProjectFeatureFlags.as_view(),
        name="project-feature-flags",
    ),
    path(
        "<slug>/link-application/",
        ProjectLinkApplication.as_view(),
        name="project-link-application",
    ),
    path(
        "<slug>/members/<pk>/edit/",
        ProjectMembershipEdit.as_view(),
        name="project-membership-edit",
    ),
    path(
        "<slug>/members/<pk>/remove/",
        ProjectMembershipRemove.as_view(),
        name="project-membership-remove",
    ),
]

redirect_urls = [
    path("", RedirectList.as_view(), name="redirect-list"),
    path("<int:pk>/", RedirectDetail.as_view(), name="redirect-detail"),
    path("<int:pk>/delete/", RedirectDelete.as_view(), name="redirect-delete"),
]

repo_urls = [
    path("", RepoList.as_view(), name="repo-list"),
    path("<repo_url>/", RepoDetail.as_view(), name="repo-detail"),
    path(
        "<repo_url>/feature-flags/",
        RepoFeatureFlags.as_view(),
        name="repo-feature-flags",
    ),
    path("<repo_url>/sign-off/", RepoSignOff.as_view(), name="repo-sign-off"),
]

researcher_urls = [
    path("<int:pk>/edit/", ResearcherEdit.as_view(), name="researcher-edit"),
]

user_urls = [
    path("", UserList.as_view(), name="user-list"),
    path("<username>/", UserDetail.as_view(), name="user-detail"),
    path("<username>/set-orgs/", UserSetOrgs.as_view(), name="user-set-orgs"),
]

workspace_urls = [
    path("", WorkspaceList.as_view(), name="workspace-list"),
    path("<slug>/", WorkspaceDetail.as_view(), name="workspace-detail"),
    path("<slug>/edit/", WorkspaceEdit.as_view(), name="workspace-edit"),
]

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("applications/", include(application_urls)),
    path("backends/", include(backend_urls)),
    path("dashboards/", include((dashboard_urls, "dashboards"), namespace="dashboard")),
    path("orgs/", include(org_urls)),
    path("projects/", include(project_urls)),
    path("redirects/", include(redirect_urls)),
    path("repos/", include(repo_urls)),
    path("researchers/", include(researcher_urls)),
    path("users/", include(user_urls)),
    path("workspaces/", include(workspace_urls)),
]
