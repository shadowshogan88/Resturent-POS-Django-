from django.urls import path

from .views import (
    categories_apply_view,
    categories_export_excel_view,
    categories_export_pdf_view,
    categories_view,
    category_add_view,
    category_delete_view,
    category_update_view,
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
    path("categories/", categories_view, name="categories"),
    path("categories/apply/", categories_apply_view, name="categories_apply"),
    path("categories/export/pdf/", categories_export_pdf_view, name="categories_export_pdf"),
    path("categories/export/excel/", categories_export_excel_view, name="categories_export_excel"),
    path("categories/add/", category_add_view, name="category_add"),
    path("categories/update/", category_update_view, name="category_update"),
    path("categories/delete/", category_delete_view, name="category_delete"),
    path("logout/", logout_view, name="logout"),
    path("<slug:page>/", page_view, name="page"),
]
