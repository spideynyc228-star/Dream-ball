from django.urls import path
from .views import create
app_name="reports"; urlpatterns=[path("new/<int:profile_id>/",create,name="create")]
