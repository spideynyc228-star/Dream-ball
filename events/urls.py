from django.urls import path
from .views import planner
app_name="events"; urlpatterns=[path("planner/",planner,name="planner")]
