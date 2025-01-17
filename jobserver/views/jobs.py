from django.core.exceptions import MultipleObjectsReturned
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import RedirectView, View

from ..authorization import CoreDeveloper, has_permission, has_role
from ..honeycomb import format_trace_link
from ..models import Job


class JobCancel(View):
    def post(self, request, *args, **kwargs):
        job = get_object_or_404(Job, identifier=self.kwargs["identifier"])

        can_cancel_job = job.job_request.created_by == request.user or has_permission(
            request.user, "job_cancel", project=job.job_request.workspace.project
        )
        if not can_cancel_job:
            raise Http404

        if job.is_completed or job.action in job.job_request.cancelled_actions:
            return redirect(job)

        job.job_request.cancelled_actions.append(job.action)
        job.job_request.save()
        return redirect(job)


class JobDetail(View):
    def get(self, request, *args, **kwargs):
        try:
            job = Job.objects.select_related(
                "job_request", "job_request__backend", "job_request__workspace"
            ).get(
                job_request__workspace__project__org__slug=self.kwargs["org_slug"],
                job_request__workspace__project__slug=self.kwargs["project_slug"],
                job_request__workspace__name=self.kwargs["workspace_slug"],
                job_request__pk=self.kwargs["pk"],
                identifier__startswith=self.kwargs["identifier"],
            )
        except (Job.DoesNotExist, MultipleObjectsReturned):
            raise Http404

        if job.identifier != self.kwargs["identifier"]:
            # redirect to the full URL if a partial identifier was used
            return redirect(job)

        can_cancel_jobs = job.job_request.created_by == request.user or has_permission(
            request.user, "job_cancel", project=job.job_request.workspace.project
        )

        honeycomb_can_view_links = has_role(self.request.user, CoreDeveloper)

        context = {
            "job": job,
            "object": job,
            "user_can_cancel_jobs": can_cancel_jobs,
            "view": self,
            "honeycomb_links": {},
        }

        honeycomb_trace_link = format_trace_link(job)
        if honeycomb_can_view_links and honeycomb_trace_link:
            context["honeycomb_links"]["Job Trace"] = honeycomb_trace_link

        if has_role(request.user, CoreDeveloper):
            template_name = "job_detail_tw.html"
        else:
            template_name = "job_detail.html"

        return TemplateResponse(request, template_name, context=context)


class JobDetailRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        job = get_object_or_404(Job, identifier=self.kwargs["identifier"])
        return job.get_absolute_url()
