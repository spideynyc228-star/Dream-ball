from django.urls import path
from . import views
app_name="students"
urlpatterns=[path("profile/",views.profile,name="profile"),path("browse/",views.browse,name="browse"),path("requests/",views.requests_page,name="requests"),path("request/<int:user_id>/",views.send_request,name="send_request"),path("request/<int:pk>/<str:action>/",views.respond_request,name="respond_request"),path("partnership/",views.partnership,name="partnership")]
