from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from dashboard.views import home

urlpatterns = [
    path("django-admin/", admin.site.urls), path("", home, name="home"),
    path("accounts/", include("accounts.urls")), path("students/", include("students.urls")),
    path("events/", include("events.urls")), path("reports/", include("reports.urls")),
    path("blog/", include("blog.urls")), path("safety/", include("safety.urls")), path("moderation/", include("moderation.urls")),
    path("dashboard/", include("dashboard.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "dashboard.errors.error_403"
handler404 = "dashboard.errors.error_404"
handler500 = "dashboard.errors.error_500"
