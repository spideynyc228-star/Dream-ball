from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [
    path("", views.dashboard, name="home"),
    path("event/", views.event_detail, name="event"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
]
