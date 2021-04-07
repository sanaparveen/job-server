from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.edit import FormMixin

from .authorization import SuperUser, has_role
from .authorization.decorators import require_superuser
from .backends import backends_to_choices, show_warning
from .forms import (
    JobRequestCreateForm,
    JobRequestSearchForm,
    OrgCreateForm,
    ProjectCreateForm,
    ResearcherFormSet,
    SettingsForm,
    WorkspaceArchiveToggleForm,
    WorkspaceCreateForm,
    WorkspaceNotificationsToggleForm,
)
from .github import get_branch_sha, get_repos_with_branches
from .models import Backend, Job, JobRequest, Org, Project, User, Workspace
from .project import get_actions, get_project, load_yaml, render_definition
from .roles import can_run_jobs


def filter_by_status(job_requests, status):
    """
    Filter JobRequests by status property

    JobRequest.status is built by "bubbling up" the status of each related Job.
    However, the construction of that property isn't easily converted to a
    QuerySet, hence this function.
    """
    if not status:
        return job_requests

    status_lut = {
        "failed": lambda r: r.status.lower() == "failed",
        "running": lambda r: r.status.lower() == "running",
        "pending": lambda r: r.status.lower() == "pending",
        "succeeded": lambda r: r.status.lower() == "succeeded",
    }
    func = status_lut[status]
    return list(filter(func, job_requests))


@method_decorator(require_superuser, name="dispatch")
class BackendDetail(DetailView):
    model = Backend
    template_name = "backend_detail.html"


@method_decorator(require_superuser, name="dispatch")
class BackendList(ListView):
    model = Backend
    template_name = "backend_list.html"


@method_decorator(require_superuser, name="dispatch")
class BackendRotateToken(View):
    def post(self, request, *args, **kwargs):
        backend = get_object_or_404(Backend, pk=self.kwargs["pk"])

        backend.rotate_token()

        return redirect(backend)


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        job_requests = JobRequest.objects.prefetch_related("jobs").order_by(
            "-created_at"
        )[:5]
        workspaces = Workspace.objects.filter(is_archived=False).order_by("name")

        context = super().get_context_data(**kwargs)
        context["job_requests"] = job_requests
        context["user_can_run_jobs"] = can_run_jobs(self.request.user)
        context["workspaces"] = workspaces
        return context


@method_decorator(user_passes_test(can_run_jobs), name="dispatch")
class JobCancel(View):
    def post(self, request, *args, **kwargs):
        job = get_object_or_404(Job, identifier=self.kwargs["identifier"])

        if job.is_finished or job.action in job.job_request.cancelled_actions:
            return redirect(job)

        job.job_request.cancelled_actions.append(job.action)
        job.job_request.save()
        return redirect(job)


class JobDetail(DetailView):
    slug_field = "identifier"
    slug_url_kwarg = "identifier"
    queryset = Job.objects.select_related(
        "job_request", "job_request__backend", "job_request__workspace"
    )
    template_name = "job_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_can_run_jobs"] = can_run_jobs(self.request.user)
        return context


class JobZombify(View):
    def dispatch(self, request, *args, **kwargs):
        if not has_role(request.user, SuperUser):
            messages.error(request, "Only admins can zombify Jobs.")
            return redirect("job-detail", identifier=self.kwargs["identifier"])

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        job = get_object_or_404(Job, identifier=self.kwargs["identifier"])

        job.status = "failed"
        job.status_message = "Job manually zombified"
        job.save()

        return redirect(job)


class JobRequestDetail(DetailView):
    model = JobRequest
    queryset = JobRequest.objects.select_related(
        "created_by", "workspace"
    ).prefetch_related("jobs")
    template_name = "job_request_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_definition"] = mark_safe(
            render_definition(
                self.object.project_definition,
                self.object.get_file_url,
            )
        )
        context["project_yaml_url"] = self.object.get_file_url("project.yaml")
        return context


class JobRequestList(FormMixin, ListView):
    form_class = JobRequestSearchForm
    paginate_by = 25
    template_name = "job_request_list.html"

    def get_context_data(self, **kwargs):
        # only get Users created via GitHub OAuth
        users = User.objects.exclude(social_auth=None)
        users = sorted(users, key=lambda u: u.name.lower())

        workspaces = Workspace.objects.filter(is_archived=False).order_by("name")

        # filter object list based on status arg
        filtered_object_list = filter_by_status(
            self.object_list, self.request.GET.get("status")
        )
        context = super().get_context_data(object_list=filtered_object_list, **kwargs)

        context["statuses"] = ["failed", "running", "pending", "succeeded"]
        context["users"] = {u.username: u.name for u in users}
        context["workspaces"] = workspaces
        return context

    def get_queryset(self):
        qs = (
            JobRequest.objects.prefetch_related("jobs")
            .select_related("workspace")
            .order_by("-pk")
        )

        q = self.request.GET.get("q")
        if q:
            qwargs = Q(jobs__action__icontains=q) | Q(jobs__identifier__icontains=q)
            try:
                q = int(q)
            except ValueError:
                qs = qs.filter(qwargs)
            else:
                # if the query looks enough like a number for int() to handle
                # it then we can look for a job number
                qs = qs.filter(qwargs | Q(jobs__pk=q))

        username = self.request.GET.get("username")
        if username:
            qs = qs.filter(created_by__username=username)

        workspace = self.request.GET.get("workspace")
        if workspace:
            qs = qs.filter(workspace_id=workspace)

        return qs

    def form_valid(self, form):
        identifier = form.cleaned_data["identifier"]

        job_request = JobRequest.objects.filter(
            identifier__icontains=identifier
        ).first()

        if not job_request:
            msg = f"Could not find a JobRequest with the identfier '{identifier}'"
            form.add_error("identifier", msg)
            return self.form_invalid(form)

        return redirect(job_request)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed POST
        variables and then check if it's valid.

        Form validity dispatch copied from Django's CBVs, modified so to
        generate object_list for when form_invalid() is called.
        """
        self.object_list = self.get_queryset()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class JobRequestZombify(View):
    def dispatch(self, request, *args, **kwargs):
        if not has_role(request.user, SuperUser):
            messages.error(request, "Only admins can zombify Jobs.")
            return redirect("job-request-detail", pk=self.kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        job_request = get_object_or_404(JobRequest, pk=self.kwargs["pk"])

        job_request.jobs.update(
            status="failed", status_message="Job manually zombified"
        )

        return redirect(job_request)


@method_decorator(require_superuser, name="dispatch")
class OrgCreate(CreateView):
    form_class = OrgCreateForm
    model = Org
    template_name = "org_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orgs"] = Org.objects.order_by("name")
        return context

    def get_success_url(self):
        return self.object.get_absolute_url()


@method_decorator(require_superuser, name="dispatch")
class OrgDetail(DetailView):
    model = Org
    slug_url_kwarg = "org_slug"
    template_name = "org_detail.html"


@method_decorator(require_superuser, name="dispatch")
class OrgList(ListView):
    model = Org
    template_name = "org_list.html"


@method_decorator(require_superuser, name="dispatch")
class ProjectCreate(CreateView):
    form_class = ProjectCreateForm
    model = Project
    template_name = "project_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.org = get_object_or_404(Org, slug=self.kwargs["org_slug"])

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        researcher_formset = ResearcherFormSet(prefix="researcher")
        return self.render_to_response(
            self.get_context_data(researcher_formset=researcher_formset)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["org"] = self.org
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form()
        researcher_formset = ResearcherFormSet(request.POST, prefix="researcher")

        form_valid = form.is_valid()
        formset_valid = researcher_formset.is_valid()
        if not (form_valid and formset_valid):
            return self.render_to_response(
                self.get_context_data(researcher_formset=researcher_formset)
            )

        project = form.save(commit=False)
        project.org = self.org
        project.save()

        researchers = researcher_formset.save()
        project.researcher_registrations.add(*researchers)

        return redirect(project)


@method_decorator(require_superuser, name="dispatch")
class ProjectDetail(DetailView):
    template_name = "project_detail.html"

    def get_object(self):
        return get_object_or_404(
            Project,
            slug=self.kwargs["project_slug"],
            org__slug=self.kwargs["org_slug"],
        )


@method_decorator(login_required, name="dispatch")
class Settings(UpdateView):
    form_class = SettingsForm
    template_name = "settings.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(self.request, "Settings saved successfully")

        return response

    def get_object(self):
        return self.request.user


class Status(View):
    def get(self, request, *args, **kwargs):
        def format_last_seen(last_seen):
            if last_seen is None:
                return "never"

            return last_seen.strftime("%Y-%m-%d %H:%M:%S")

        def get_stats(backend):
            acked = backend.job_requests.acked().count()
            unacked = backend.job_requests.unacked().count()

            try:
                last_seen = (
                    backend.stats.order_by("-api_last_seen").first().api_last_seen
                )
            except AttributeError:
                last_seen = None

            return {
                "name": backend.display_name,
                "last_seen": format_last_seen(last_seen),
                "queue": {
                    "acked": acked,
                    "unacked": unacked,
                },
                "show_warning": show_warning(last_seen),
            }

        backends = Backend.objects.all()
        context = {"backends": [get_stats(b) for b in backends]}

        return TemplateResponse(request, "status.html", context)


@method_decorator(user_passes_test(can_run_jobs), name="dispatch")
class WorkspaceArchiveToggle(View):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(Workspace, name=self.kwargs["name"])

        form = WorkspaceArchiveToggleForm(request.POST)
        form.is_valid()

        workspace.is_archived = form.cleaned_data["is_archived"]
        workspace.save()

        return redirect("/")


@method_decorator(user_passes_test(can_run_jobs), name="dispatch")
class WorkspaceCreate(CreateView):
    form_class = WorkspaceCreateForm
    model = Workspace
    template_name = "workspace_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.repos_with_branches = sorted(
            get_repos_with_branches(), key=lambda r: r["name"].lower()
        )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by = self.request.user
        instance.save()

        return redirect(instance)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["repos_with_branches"] = self.repos_with_branches
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["repos_with_branches"] = self.repos_with_branches
        return kwargs


class WorkspaceDetail(CreateView):
    form_class = JobRequestCreateForm
    model = JobRequest
    template_name = "workspace_detail.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.workspace = Workspace.objects.get(name=self.kwargs["name"])
        except Workspace.DoesNotExist:
            return redirect("/")

        self.user_can_run_jobs = can_run_jobs(request.user)

        self.show_details = (
            request.user.is_authenticated
            and self.user_can_run_jobs
            and not self.workspace.is_archived
        )

        if not self.show_details:
            # short-circuit for logged out users to avoid the hop to grab
            # actions from GitHub
            self.actions = []
            return super().dispatch(request, *args, **kwargs)

        action_status_lut = self.workspace.get_action_status_lut()

        # build actions as list or render the exception to the page
        try:
            self.project = get_project(
                self.workspace.repo_name,
                self.workspace.branch,
            )
            data = load_yaml(self.project)
        except Exception as e:
            self.actions = []
            # this is a bit nasty, need to mirror what get/post would set up for us
            self.object = None
            context = self.get_context_data(actions_error=str(e))
            return self.render_to_response(context=context)

        self.actions = list(get_actions(data, action_status_lut))
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        sha = get_branch_sha(self.workspace.repo_name, self.workspace.branch)

        if has_role(self.request.user, SuperUser):
            # Use the form data to decide which backend to use for superusers.
            backend = Backend.objects.get(name=form.cleaned_data.pop("backend"))
        else:
            # For non-superusers we're only exposing one backend currently.
            backend = Backend.objects.get(name="tpp")

        backend.job_requests.create(
            workspace=self.workspace,
            created_by=self.request.user,
            sha=sha,
            project_definition=self.project,
            **form.cleaned_data,
        )
        return redirect("workspace-logs", name=self.workspace.name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actions"] = self.actions
        context["branch"] = self.workspace.branch
        context["latest_job_request"] = self.get_latest_job_request()
        context["show_details"] = self.show_details
        context["user_can_run_jobs"] = self.user_can_run_jobs
        context["workspace"] = self.workspace
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actions"] = [a["name"] for a in self.actions]

        if has_role(self.request.user, SuperUser):
            # TODO: move to ModelForm declaration once all users can pick backends
            backends = Backend.objects.all()
            backend_choices = backends_to_choices(backends)
            kwargs["backends"] = backend_choices

        return kwargs

    def get_initial(self):
        # derive will_notify for the JobRequestCreateForm from the Workspace
        # setting as a default for the form which the user can override.
        return {"will_notify": self.workspace.should_notify}

    def get_latest_job_request(self):
        return (
            self.workspace.job_requests.prefetch_related("jobs")
            .order_by("-created_at")
            .first()
        )

    def post(self, request, *args, **kwargs):
        if self.workspace.is_archived:
            msg = (
                "You cannot create Jobs for an archived Workspace."
                "Please contact an admin if you need to have it unarchved."
            )
            messages.error(request, msg)
            return redirect(self.workspace)

        return super().post(request, *args, **kwargs)


class WorkspaceLog(ListView):
    paginate_by = 25
    template_name = "workspace_log.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.workspace = Workspace.objects.get(name=self.kwargs["name"])
        except Workspace.DoesNotExist:
            return redirect("/")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_can_run_jobs"] = can_run_jobs(self.request.user)
        context["workspace"] = self.workspace
        return context

    def get_queryset(self):
        qs = (
            JobRequest.objects.filter(workspace=self.workspace)
            .prefetch_related("jobs")
            .select_related("workspace")
            .order_by("-pk")
        )

        q = self.request.GET.get("q")
        if q:
            qwargs = Q(jobs__action__icontains=q) | Q(jobs__identifier__icontains=q)
            try:
                q = int(q)
            except ValueError:
                qs = qs.filter(qwargs)
            else:
                # if the query looks enough like a number for int() to handle
                # it then we can look for a job number
                qs = qs.filter(qwargs | Q(jobs__pk=q))

        return qs


@method_decorator(user_passes_test(can_run_jobs), name="dispatch")
class WorkspaceNotificationsToggle(View):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(Workspace, name=self.kwargs["name"])

        form = WorkspaceNotificationsToggleForm(data=request.POST)
        form.is_valid()

        workspace.should_notify = form.cleaned_data["should_notify"]
        workspace.save()

        return redirect(workspace)


@method_decorator(user_passes_test(can_run_jobs), name="dispatch")
class WorkspaceReleaseView(View):
    def get(self, request, name, release):
        return f"release page for {name}/{release}"  # pragma: no cover
