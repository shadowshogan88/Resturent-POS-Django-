from django.urls import path

from .views import (
    dashboard_view,
    login_view,
    logout_view,
    page_view,
    register_view,
    username_check_view,
)


urlpatterns = [
    path("", login_view, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("htmx/username-check/", username_check_view, name="username_check"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("logout/", logout_view, name="logout"),
    path("<slug:page>/", page_view, name="page"),
]
