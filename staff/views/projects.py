from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from applications.models import Application
from jobserver.authorization import CoreDeveloper
from jobserver.authorization.decorators import require_role
from jobserver.authorization.utils import roles_for
from jobserver.models import Org, Project, ProjectMembership, User

from ..forms import (
    ProjectAddMemberForm,
    ProjectCreateForm,
    ProjectEditForm,
    ProjectFeatureFlagsForm,
    ProjectLinkApplicationForm,
    ProjectMembershipForm,
)


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectAddMember(FormView):
    form_class = ProjectAddMemberForm
    template_name = "staff/project_membership_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=self.kwargs["slug"])

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        roles = form.cleaned_data["roles"]
        users = form.cleaned_data["users"]

        with transaction.atomic():
            for user in users:
                self.project.memberships.create(
                    user=user,
                    created_by=self.request.user,
                    roles=roles,
                )

        return redirect(self.project.get_staff_url())

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "members": self.project.members.order_by(Lower("username")),
            "project": self.project,
        }

    def get_form_kwargs(self):
        members = self.project.members.values_list("pk", flat=True)
        return super().get_form_kwargs() | {
            "available_roles": roles_for(ProjectMembership),
            "users": User.objects.exclude(pk__in=members),
        }

    def get_initial(self):
        return super().get_initial() | {
            "users": self.project.members.values_list("pk", flat=True),
        }


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectCreate(CreateView):
    form_class = ProjectCreateForm
    template_name = "staff/project_create.html"

    def form_valid(self, form):
        project = form.save(commit=False)
        project.created_by = self.request.user
        project.save()

        return redirect(project.get_staff_url())


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectDetail(DetailView):
    model = Project
    template_name = "staff/project_detail.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "application": self.object.applications.first(),
            "memberships": self.object.memberships.select_related("user").order_by(
                Lower("user__username")
            ),
            "redirects": self.object.redirects.order_by("old_url"),
            "workspaces": self.object.workspaces.order_by("name"),
        }


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectEdit(UpdateView):
    form_class = ProjectEditForm
    model = Project
    template_name = "staff/project_edit.html"

    @transaction.atomic()
    def form_valid(self, form):
        # look up the original object from the database because the form will
        # mutation self.object under us
        old = self.get_object()

        new = form.save()

        # check changed_data here instead of comparing self.object.project to
        # new.project because self.object is mutated when ModelForm._post_clean
        # updates the instance it was passed.  This is because form.instance is
        # set from the passed in self.object.
        if {"org", "slug"} & set(form.changed_data):
            new.redirects.create(
                created_by=self.request.user,
                old_url=old.get_absolute_url(),
            )

        return redirect(new.get_staff_url())

    def get_context_data(self, **kwargs):
        # we don't have a nice way to override the type of text input
        # components yet so doing this here is a bit of a hack because we can't
        # construct dicts in a template
        return super().get_context_data(**kwargs) | {
            "extra_field_attributes": {"type": "number"},
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            "users": User.objects.all(),
        }


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectFeatureFlags(TemplateView):
    template_name = "staff/project_feature_flags.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=self.kwargs["slug"])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        enabled_count = self.project.workspaces.filter(
            uses_new_release_flow=True
        ).count()
        disabled_count = self.project.workspaces.filter(
            uses_new_release_flow=False
        ).count()

        return super().get_context_data(**kwargs) | {
            "project": self.project,
            "enabled_count": enabled_count,
            "disabled_count": disabled_count,
        }

    def post(self, request, *args, **kwargs):
        form = ProjectFeatureFlagsForm(request.POST)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        # the form validation ensures this is enable|disable
        enable = form.cleaned_data["flip_to"] == "enable"
        self.project.workspaces.update(uses_new_release_flow=enable)

        return redirect(self.project.get_staff_feature_flags_url())


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectLinkApplication(UpdateView):
    form_class = ProjectLinkApplicationForm
    model = Project
    template_name = "staff/project_link_application.html"

    def form_valid(self, form):
        application = form.cleaned_data["application"]

        self.object.applications.add(application)
        self.object.save()

        return redirect(self.object.get_staff_url())

    def get_context_data(self, **kwargs):
        # get applications that we can consider done, or at least not clearly
        # not-done
        ignored_statuses = [
            Application.Statuses.ONGOING,
            Application.Statuses.REJECTED,
        ]
        applications = (
            Application.objects.filter(project=None)
            .exclude(status__in=ignored_statuses)
            .select_related("created_by")
            .order_by("-created_at")
        )

        return super().get_context_data(**kwargs) | {
            "applications": applications,
        }


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectList(ListView):
    queryset = Project.objects.select_related("org").order_by("number", Lower("name"))
    template_name = "staff/project_list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "orgs": Org.objects.order_by("name"),
            "q": self.request.GET.get("q", ""),
        }

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(number__icontains=q))

        org = self.request.GET.get("org")
        if org:
            qs = qs.filter(org__slug=org)
        return qs


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectMembershipEdit(UpdateView):
    context_object_name = "membership"
    form_class = ProjectMembershipForm
    model = ProjectMembership
    template_name = "staff/project_membership_edit.html"

    def form_valid(self, form):
        self.object.roles = form.cleaned_data["roles"]
        self.object.save()

        return redirect(self.object.project.get_staff_url())

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)

        # ProjectMembershipForm isn't a ModelForm so don't pass instance to it
        del kwargs["instance"]

        kwargs["available_roles"] = roles_for(ProjectMembership)

        return kwargs

    def get_initial(self):
        return super().get_initial() | {
            "roles": self.object.roles,
        }

    def get_object(self):
        return get_object_or_404(
            ProjectMembership,
            project__slug=self.kwargs["slug"],
            pk=self.kwargs["pk"],
        )


@method_decorator(require_role(CoreDeveloper), name="dispatch")
class ProjectMembershipRemove(View):
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, slug=self.kwargs["slug"])
        username = request.POST.get("username", None)

        try:
            project.memberships.get(user__username=username).delete()
        except ProjectMembership.DoesNotExist:
            pass

        messages.success(request, f"Removed {username} from {project.title}")
        return redirect(project.get_staff_url())
