from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, UserLoginView
app_name="accounts"
urlpatterns=[path("register/", register, name="register"), path("login/", UserLoginView.as_view(), name="login"), path("logout/", LogoutView.as_view(), name="logout")]
