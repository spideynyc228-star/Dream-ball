from pathlib import Path

from django.http import FileResponse, Http404
from django.urls import path
from django.views.generic import TemplateView


def checklist_download(request):
    checklist = Path(__file__).resolve().parents[1] / "docs" / "Digital_Safety_Checklist.pdf"
    if not checklist.exists():
        raise Http404("Safety checklist is not available.")
    return FileResponse(checklist.open("rb"), as_attachment=True, filename="Digital_Safety_Checklist.pdf")


app_name = "safety"
urlpatterns = [path("", TemplateView.as_view(template_name="safety/index.html"), name="index"), path("checklist/", checklist_download, name="checklist")]
