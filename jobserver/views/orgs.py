from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import DetailView, ListView

from ..models import Org, Workspace


class OrgDetail(DetailView):
    template_name = "org_detail.html"

    def get(self, request, *args, **kwargs):
        slug = self.kwargs["org_slug"]

        try:
            org = Org.objects.get(slug=slug)
        except Org.DoesNotExist:
            # we used to serve up Workspaces at the root URL but have moved
            # them under their relevant Orgs & Projects.  So attempt to
            # redirect requests to a valid Workspace here for a while.

            try:
                workspace = Workspace.objects.get(name=slug)
            except Workspace.DoesNotExist:
                raise Http404

            return redirect(workspace)

        projects = org.projects.order_by("number", Lower("name"))

        return TemplateResponse(
            request,
            "org_detail.html",
            context={
                "org": org,
                "projects": projects,
            },
        )


class OrgList(ListView):
    queryset = Org.objects.order_by("name")
    template_name = "org_list.html"
