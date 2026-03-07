import csv
import json
from io import StringIO
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from collections import defaultdict
from django.db import models, transaction
from django.db.models import Count, Q, Sum
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from .models import (
    AuditLog,
    Addon,
    Category,
    Customer,
    DiningTable,
    Item,
    ItemAddon,
    ItemVariation,
    Order,
    OrderItem,
    PrintSetting,
    Role,
    RolePermission,
    StoreSetting,
    Tax,
    UserPermissionOverride,
)


User = get_user_model()
POS_TAX_RATE = Decimal("18.00")
POS_SERVICE_CHARGE = Decimal("0.00")
DEFAULT_ROLE_NAMES = [
    "Admin",
    "Supervisor",
    "Cashier",
    "Chef",
    "Waiter",
    "Accountant",
    "System Operator",
]
ROLE_PERMISSION_MODULES = [
    ("dashboard", "Dashboard"),
    ("pos", "POS"),
    ("products", "Products"),
    ("categories", "Categories"),
    ("customers", "Customers"),
    ("hold_resume_sale", "Hold/Resume Sale"),
    ("refund_return", "Refund / Return"),
    ("reports", "Reports"),
    ("settings", "Settings"),
]
ROLE_PERMISSION_ACTIONS = [
    ("view", "can_view", "View"),
    ("add", "can_add", "Add"),
    ("edit", "can_edit", "Edit"),
    ("delete", "can_delete", "Delete"),
    ("export", "can_export", "Export"),
    ("approve_void", "can_approve_void", "Approved/Void"),
]
CURRENCY_META = {
    "USD": ("US Dollar", "$"),
    "AED": ("UAE Dirham", "AED"),
    "EUR": ("Euro", "EUR"),
    "INR": ("Indian Rupee", "Rs"),
}
AUDIT_ACTION_LABELS = {
    "system_enabled": "System Enabled",
    "login_success": "Login Success",
    "login_failed": "Login Failed",
    "logout": "Logout",
    "item_created": "Product Created",
    "item_updated": "Product Updated",
    "item_deleted": "Product Deleted",
    "order_placed": "Order Placed",
    "order_drafted": "Order Drafted",
    "order_cancelled": "Order Cancelled",
    "print_settings_updated": "Print Settings Updated",
    "store_settings_updated": "Store Settings Updated",
    "table_created": "Table Created",
    "table_updated": "Table Updated",
    "table_deleted": "Table Deleted",
    "user_created": "User Created",
    "user_updated": "User Updated",
    "user_deleted": "User Deleted",
    "user_permissions_updated": "User Permissions Updated",
    "role_created": "Role Created",
    "role_permissions_updated": "Role Permissions Updated",
    "category_created": "Category Created",
    "category_updated": "Category Updated",
    "category_deleted": "Category Deleted",
    "customer_created": "Customer Created",
    "customer_updated": "Customer Updated",
    "kitchen_started": "Kitchen Started",
    "kitchen_paused": "Kitchen Paused",
    "kitchen_completed": "Kitchen Completed",
}
AUDIT_ACTION_ICONS = {
    "system_enabled": "icon-settings",
    "login_success": "icon-log-in",
    "login_failed": "icon-circle-alert",
    "logout": "icon-log-out",
    "item_created": "icon-chef-hat",
    "item_updated": "icon-square-pen",
    "item_deleted": "icon-trash-2",
    "order_placed": "icon-shopping-bag",
    "order_drafted": "icon-file-stack",
    "order_cancelled": "icon-ban",
    "print_settings_updated": "icon-printer",
    "store_settings_updated": "icon-warehouse",
    "table_created": "icon-concierge-bell",
    "table_updated": "icon-pencil-line",
    "table_deleted": "icon-trash-2",
    "user_created": "icon-user-round-plus",
    "user_updated": "icon-user-pen",
    "user_deleted": "icon-user-x",
    "user_permissions_updated": "icon-shield-check",
    "role_created": "icon-badge-plus",
    "role_permissions_updated": "icon-shield",
    "category_created": "icon-layers-2",
    "category_updated": "icon-square-pen",
    "category_deleted": "icon-trash-2",
    "customer_created": "icon-user-round-plus",
    "customer_updated": "icon-user-round-cog",
    "kitchen_started": "icon-chef-hat",
    "kitchen_paused": "icon-pause",
    "kitchen_completed": "icon-check-check",
}


def _get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or None


def _log_audit_event(request, action, module, description, target="", actor=None):
    actor_user = actor
    if actor_user is None and getattr(request, "user", None) is not None and request.user.is_authenticated:
        actor_user = request.user

    AuditLog.objects.create(
        actor=actor_user,
        actor_name=(actor_user.full_name if actor_user and actor_user.full_name else actor_user.username) if actor_user else "",
        actor_role=getattr(actor_user, "role", "") if actor_user else "",
        action=action,
        module=module,
        description=description,
        target=target,
        ip_address=_get_client_ip(request) if request is not None else None,
    )


def _escape_pdf_text(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines, title="Categories Export"):
    # Minimal single-page PDF generator without external dependencies.
    content_lines = ["BT", "/F1 11 Tf", "50 800 Td"]
    content_lines.append(f"({_escape_pdf_text(title)}) Tj")
    content_lines.append("0 -20 Td")

    max_lines = 35
    for line in lines[:max_lines]:
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
        content_lines.append("0 -18 Td")
    content_lines.append("ET")
    stream_data = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >> endobj\n"
    )
    objects.append(
        b"4 0 obj << /Length " + str(len(stream_data)).encode() + b" >> stream\n" +
        stream_data + b"\nendstream endobj\n"
    )
    objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj
    xref_offset = len(pdf)
    pdf += b"xref\n0 6\n0000000000 65535 f \n"
    for i in range(1, 6):
        pdf += f"{offsets[i]:010d} 00000 n \n".encode()
    pdf += b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n"
    pdf += str(xref_offset).encode() + b"\n%%EOF"
    return pdf


def _filtered_sorted_categories_from_params(params):
    raw_category_ids = params.getlist("category")
    selected_category_ids = []
    for value in raw_category_ids:
        try:
            selected_category_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_status = params.get("status", "").strip().title()
    sort_by = params.get("sort_by", "").strip().lower() or "newest"
    sort_map = {
        "newest": ("-created_on", "-id"),
        "oldest": ("created_on", "id"),
        "ascending": ("name",),
        "descending": ("-name",),
    }
    if sort_by not in sort_map:
        sort_by = "newest"

    queryset = Category.objects.all()
    if selected_category_ids:
        queryset = queryset.filter(id__in=selected_category_ids)
    if selected_status in dict(Category.STATUS_CHOICES):
        queryset = queryset.filter(status=selected_status)
    queryset = queryset.order_by(*sort_map[sort_by])

    return queryset, selected_category_ids, selected_status, sort_by


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        agree_terms = request.POST.get("agree_terms")

        if not username or not password or not confirm_password:
            messages.error(request, "All required fields must be filled.")
        elif password != confirm_password:
            messages.error(request, "Password and confirm password do not match.")
        elif not agree_terms:
            messages.error(request, "You must agree to Terms and Privacy Policy.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
        else:
            # Model requires unique email and full_name; fill them from username.
            email = f"{username.lower()}@local.pos"
            if User.objects.filter(email=email).exists():
                email = f"{username.lower()}_{User.objects.count() + 1}@local.pos"

            User.objects.create_user(
                username=username,
                full_name=username,
                email=email,
                password=password,
                role="User",
            )
            messages.success(request, "Registration successful. Please sign in.")
            return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")

        if not username or not password:
            messages.error(request, "Username and password are required.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is None:
                _log_audit_event(
                    request,
                    action="login_failed",
                    module="Authentication",
                    description=f"Failed login attempt for username '{username or 'Unknown'}'.",
                    target=username or "Unknown",
                )
                messages.error(request, "Invalid username or password.")
            else:
                login(request, user)
                _log_audit_event(
                    request,
                    action="login_success",
                    module="Authentication",
                    description=f"User {user.full_name or user.username} signed in successfully.",
                    target=user.username,
                    actor=user,
                )
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, "Login successful.")
                return redirect("dashboard")

    return render(request, "login.html")


def username_check_view(request):
    username = request.GET.get("username", "").strip()
    context = {
        "username": username,
        "checked": bool(username),
        "is_taken": False,
    }
    if username:
        context["is_taken"] = User.objects.filter(username=username).exists()
    return render(request, "partials/username_check.html", context)


@login_required(login_url="login")
def categories_view(request):
    queryset, selected_category_ids, selected_status, sort_by = _filtered_sorted_categories_from_params(request.GET)

    sort_label_map = {
        "newest": "Newest",
        "oldest": "Oldest",
        "ascending": "Ascending",
        "descending": "Descending",
    }

    context = {
        "categories": queryset,
        "all_categories": Category.objects.all(),
        "selected_category_ids": {str(value) for value in selected_category_ids},
        "selected_status": selected_status,
        "status_choices": Category.STATUS_CHOICES,
        "sort_by": sort_by,
        "sort_label": sort_label_map[sort_by],
    }
    if request.headers.get("HX-Request"):
        return render(request, "partials/categories_table.html", context)
    return render(request, "categories.html", context)


@login_required(login_url="login")
def categories_export_excel_view(request):
    queryset, _, _, _ = _filtered_sorted_categories_from_params(request.GET)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Category", "No of Items", "Created On", "Status"])
    for category in queryset:
        writer.writerow([
            category.name,
            category.items_count,
            category.created_on.strftime("%Y-%m-%d"),
            category.status,
        ])

    response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="categories_export.csv"'
    return response


@login_required(login_url="login")
def categories_export_pdf_view(request):
    queryset, _, _, _ = _filtered_sorted_categories_from_params(request.GET)

    lines = [
        f"{idx}. {category.name} | Items: {category.items_count} | "
        f"Created: {category.created_on.strftime('%Y-%m-%d')} | Status: {category.status}"
        for idx, category in enumerate(queryset, start=1)
    ]
    if not lines:
        lines = ["No categories found for the selected filters."]

    pdf_bytes = _build_simple_pdf(lines, title="Categories Export")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="categories_export.pdf"'
    return response


def _valid_category_status(value):
    return value if value in dict(Category.STATUS_CHOICES) else "Active"


@login_required(login_url="login")
def categories_apply_view(request):
    if request.method != "POST":
        return redirect("categories")

    raw_category_ids = request.POST.getlist("category")
    selected_ids = []
    for value in raw_category_ids:
        try:
            selected_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_status = request.POST.get("status", "").strip().title()
    sort_by = request.POST.get("sort_by", "").strip().lower() or "newest"
    valid_sort = {"newest", "oldest", "ascending", "descending"}
    if sort_by not in valid_sort:
        sort_by = "newest"

    if not selected_ids and not selected_status:
        messages.error(request, "Please select at least one category or status.")
        return redirect("categories")

    if selected_ids and selected_status in dict(Category.STATUS_CHOICES):
        updated = Category.objects.filter(id__in=selected_ids).update(status=selected_status)
        messages.success(request, f"{updated} category status updated to {selected_status}.")
    elif selected_ids and not selected_status:
        messages.error(request, "Please select a status to update selected categories.")
    elif selected_status in dict(Category.STATUS_CHOICES):
        # No category selected: treat it as filter only.
        messages.info(request, f"Filtered by status: {selected_status}.")
    else:
        messages.error(request, "Invalid status selected.")
        return redirect("categories")

    params = []
    for category_id in selected_ids:
        params.append(("category", category_id))
    if selected_status in dict(Category.STATUS_CHOICES):
        params.append(("status", selected_status))
    params.append(("sort_by", sort_by))

    query = urlencode(params, doseq=True)
    target = reverse("categories")
    if query:
        return redirect(f"{target}?{query}")
    return redirect(target)


@login_required(login_url="login")
def category_add_view(request):
    if request.method != "POST":
        return redirect("categories")

    name = request.POST.get("name", "").strip()
    items_count = request.POST.get("items_count", "").strip()
    status = _valid_category_status(request.POST.get("status", "").strip())
    image = request.FILES.get("category_image")

    if not name:
        messages.error(request, "Category name is required.")
        return redirect("categories")
    if Category.objects.filter(name__iexact=name).exists():
        messages.error(request, "Category name already exists.")
        return redirect("categories")

    try:
        items_count_value = int(items_count) if items_count else 0
        if items_count_value < 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Items count must be a non-negative number.")
        return redirect("categories")

    category = Category.objects.create(
        name=name,
        image=image,
        items_count=items_count_value,
        status=status,
        created_on=timezone.now().date(),
    )
    _log_audit_event(
        request,
        action="category_created",
        module="Categories",
        description=f"Category '{category.name}' created with status {category.status}.",
        target=category.name,
    )
    messages.success(request, "Category added successfully.")
    return redirect("categories")


@login_required(login_url="login")
def category_update_view(request):
    if request.method != "POST":
        return redirect("categories")

    category_id = request.POST.get("category_id")
    try:
        category = Category.objects.get(id=category_id)
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Category not found.")
        return redirect("categories")

    name = request.POST.get("name", "").strip()
    items_count = request.POST.get("items_count", "").strip()
    status = _valid_category_status(request.POST.get("status", "").strip())
    image = request.FILES.get("category_image")

    if not name:
        messages.error(request, "Category name is required.")
        return redirect("categories")
    if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
        messages.error(request, "Category name already exists.")
        return redirect("categories")

    try:
        items_count_value = int(items_count) if items_count else category.items_count
        if items_count_value < 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Items count must be a non-negative number.")
        return redirect("categories")

    category.name = name
    category.items_count = items_count_value
    category.status = status
    if image:
        category.image = image
    category.save()
    _log_audit_event(
        request,
        action="category_updated",
        module="Categories",
        description=f"Category '{category.name}' updated to status {category.status}.",
        target=category.name,
    )

    messages.success(request, "Category updated successfully.")
    return redirect("categories")


@login_required(login_url="login")
def category_delete_view(request):
    if request.method != "POST":
        return redirect("categories")

    category_id = request.POST.get("category_id")
    try:
        category = Category.objects.get(id=category_id)
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Category not found.")
        return redirect("categories")

    category_name = category.name
    category.delete()
    _log_audit_event(
        request,
        action="category_deleted",
        module="Categories",
        description=f"Category '{category_name}' was deleted.",
        target=category_name,
    )
    messages.success(request, "Category deleted successfully.")
    return redirect("categories")


def _filtered_sorted_addons_from_params(params):
    raw_item_ids = params.getlist("item")
    selected_item_ids = []
    for value in raw_item_ids:
        try:
            selected_item_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    raw_addon_ids = params.getlist("addon")
    selected_addon_ids = []
    for value in raw_addon_ids:
        try:
            selected_addon_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_status = params.get("status", "").strip().title()
    sort_by = params.get("sort_by", "").strip().lower() or "newest"
    sort_map = {
        "newest": ("-created_on", "-id"),
        "oldest": ("created_on", "id"),
        "ascending": ("name",),
        "descending": ("-name",),
    }
    if sort_by not in sort_map:
        sort_by = "newest"

    queryset = Addon.objects.select_related("item").all()
    if selected_item_ids:
        queryset = queryset.filter(item_id__in=selected_item_ids)
    if selected_addon_ids:
        queryset = queryset.filter(id__in=selected_addon_ids)
    if selected_status in dict(Addon.STATUS_CHOICES):
        queryset = queryset.filter(status=selected_status)
    queryset = queryset.order_by(*sort_map[sort_by])

    return queryset, selected_item_ids, selected_addon_ids, selected_status, sort_by


def _valid_addon_status(value):
    return value if value in dict(Addon.STATUS_CHOICES) else "Active"


@login_required(login_url="login")
def addons_view(request):
    queryset, selected_item_ids, selected_addon_ids, selected_status, sort_by = _filtered_sorted_addons_from_params(request.GET)
    sort_label_map = {
        "newest": "Newest",
        "oldest": "Oldest",
        "ascending": "Ascending",
        "descending": "Descending",
    }
    context = {
        "addons": queryset,
        "all_items": Category.objects.all(),
        "all_addons": Addon.objects.all(),
        "selected_item_ids": {str(v) for v in selected_item_ids},
        "selected_addon_ids": {str(v) for v in selected_addon_ids},
        "selected_status": selected_status,
        "status_choices": Addon.STATUS_CHOICES,
        "sort_by": sort_by,
        "sort_label": sort_label_map[sort_by],
    }
    if request.headers.get("HX-Request"):
        return render(request, "partials/addons_table.html", context)
    return render(request, "addons.html", context)


@login_required(login_url="login")
def addons_export_excel_view(request):
    queryset, _, _, _, _ = _filtered_sorted_addons_from_params(request.GET)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Item", "Addon", "Price", "Created On", "Status"])
    for addon in queryset:
        writer.writerow([
            addon.item.name if addon.item else "",
            addon.name,
            str(addon.price),
            addon.created_on.strftime("%Y-%m-%d"),
            addon.status,
        ])
    response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="addons_export.csv"'
    return response


@login_required(login_url="login")
def addons_export_pdf_view(request):
    queryset, _, _, _, _ = _filtered_sorted_addons_from_params(request.GET)
    lines = [
        f"{idx}. {addon.item.name if addon.item else '-'} | {addon.name} | Price: {addon.price} | "
        f"Created: {addon.created_on.strftime('%Y-%m-%d')} | Status: {addon.status}"
        for idx, addon in enumerate(queryset, start=1)
    ]
    if not lines:
        lines = ["No addons found for the selected filters."]
    pdf_bytes = _build_simple_pdf(lines, title="Addons Export")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="addons_export.pdf"'
    return response


@login_required(login_url="login")
def addon_add_view(request):
    if request.method != "POST":
        return redirect("addons")

    item_id = request.POST.get("item_id", "").strip()
    name = request.POST.get("name", "").strip()
    price_raw = request.POST.get("price", "")
    description = request.POST.get("description", "").strip()
    status = _valid_addon_status(request.POST.get("status", "").strip())
    image = request.FILES.get("image")

    if not item_id:
        messages.error(request, "Item is required.")
        return redirect("addons")
    try:
        item = Category.objects.get(id=int(item_id))
    except (Category.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Selected item not found.")
        return redirect("addons")

    if not name:
        messages.error(request, "Addon name is required.")
        return redirect("addons")
    if Addon.objects.filter(name__iexact=name, item=item).exists():
        messages.error(request, "This addon already exists for the selected item.")
        return redirect("addons")
    try:
        price = _parse_positive_decimal(price_raw, "Price")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("addons")

    addon = Addon.objects.create(
        item=item,
        name=name,
        image=image,
        price=price,
        description=description,
        status=status,
        created_on=timezone.now().date(),
    )
    _log_audit_event(
        request,
        action="item_created",
        module="Addons",
        description=f"Addon '{addon.name}' created for category '{item.name}'.",
        target=addon.name,
    )
    messages.success(request, "Addon added successfully.")
    return redirect("addons")


@login_required(login_url="login")
def addon_update_view(request):
    if request.method != "POST":
        return redirect("addons")

    addon_id = request.POST.get("addon_id")
    try:
        addon = Addon.objects.get(id=addon_id)
    except (Addon.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Addon not found.")
        return redirect("addons")

    item_id = request.POST.get("item_id", "").strip()
    name = request.POST.get("name", "").strip()
    price_raw = request.POST.get("price", "")
    description = request.POST.get("description", "").strip()
    status = _valid_addon_status(request.POST.get("status", "").strip())
    image = request.FILES.get("image")

    try:
        item = Category.objects.get(id=int(item_id))
    except (Category.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Selected item not found.")
        return redirect("addons")

    if not name:
        messages.error(request, "Addon name is required.")
        return redirect("addons")
    if Addon.objects.filter(name__iexact=name, item=item).exclude(id=addon.id).exists():
        messages.error(request, "This addon already exists for the selected item.")
        return redirect("addons")
    try:
        price = _parse_positive_decimal(price_raw, "Price")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("addons")

    addon.item = item
    addon.name = name
    addon.price = price
    addon.description = description
    addon.status = status
    if image:
        addon.image = image
    addon.save()
    _log_audit_event(
        request,
        action="item_updated",
        module="Addons",
        description=f"Addon '{addon.name}' updated for category '{item.name}'.",
        target=addon.name,
    )
    messages.success(request, "Addon updated successfully.")
    return redirect("addons")


@login_required(login_url="login")
def addon_delete_view(request):
    if request.method != "POST":
        return redirect("addons")

    addon_id = request.POST.get("addon_id")
    try:
        addon = Addon.objects.get(id=addon_id)
    except (Addon.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Addon not found.")
        return redirect("addons")
    addon_name = addon.name
    addon.delete()
    _log_audit_event(
        request,
        action="item_deleted",
        module="Addons",
        description=f"Addon '{addon_name}' was deleted.",
        target=addon_name,
    )
    messages.success(request, "Addon deleted successfully.")
    return redirect("addons")


@login_required(login_url="login")
def addons_apply_view(request):
    if request.method != "POST":
        return redirect("addons")

    selected_item_ids = []
    for value in request.POST.getlist("item"):
        try:
            selected_item_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_addon_ids = []
    for value in request.POST.getlist("addon"):
        try:
            selected_addon_ids.append(int(value))
        except (TypeError, ValueError):
            continue

    selected_status = request.POST.get("status", "").strip().title()
    sort_by = request.POST.get("sort_by", "").strip().lower() or "newest"
    if sort_by not in {"newest", "oldest", "ascending", "descending"}:
        sort_by = "newest"

    if selected_addon_ids and selected_status in dict(Addon.STATUS_CHOICES):
        updated = Addon.objects.filter(id__in=selected_addon_ids).update(status=selected_status)
        messages.success(request, f"{updated} addon status updated to {selected_status}.")
    elif selected_addon_ids and not selected_status:
        messages.error(request, "Please select a status to update selected addons.")
    elif selected_status and selected_status not in dict(Addon.STATUS_CHOICES):
        messages.error(request, "Invalid status selected.")
        return redirect("addons")

    params = []
    for item_id in selected_item_ids:
        params.append(("item", item_id))
    for addon_id in selected_addon_ids:
        params.append(("addon", addon_id))
    if selected_status in dict(Addon.STATUS_CHOICES):
        params.append(("status", selected_status))
    params.append(("sort_by", sort_by))
    query = urlencode(params, doseq=True)
    target = reverse("addons")
    return redirect(f"{target}?{query}" if query else target)


def _parse_positive_decimal(raw_value, field_label):
    value = (raw_value or "").strip().replace("$", "").replace(",", "")
    try:
        decimal_value = Decimal(value)
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_label} must be a valid number.")
    if decimal_value <= 0:
        raise ValueError(f"{field_label} must be greater than 0.")
    return _quantize_money(decimal_value)


def _valid_customer_status(value):
    return value if value in dict(Customer.STATUS_CHOICES) else "Active"


def _valid_customer_gender(value):
    return value if value in dict(Customer.GENDER_CHOICES) else ""


def _extract_item_child_rows(post_data, name_key, price_key):
    names = post_data.getlist(name_key)
    prices = post_data.getlist(price_key)
    rows = []
    max_len = max(len(names), len(prices))
    for idx in range(max_len):
        name = names[idx].strip() if idx < len(names) and names[idx] else ""
        price_raw = prices[idx].strip() if idx < len(prices) and prices[idx] else ""
        if not name and not price_raw:
            continue
        if not name or not price_raw:
            raise ValueError("All variation/add-on rows must have both name and price.")
        price = _parse_positive_decimal(price_raw, "Row price")
        rows.append((name, price))
    return rows


def _validate_unique_child_names(rows, label):
    seen = set()
    for name, _ in rows:
        key = name.casefold()
        if key in seen:
            raise ValueError(f"Duplicate {label} name '{name}' is not allowed.")
        seen.add(key)


def _quantize_money(value):
    return value.quantize(Decimal("0.01"))


def _safe_file_url(field_file):
    if not field_file:
        return ""
    try:
        return field_file.url
    except ValueError:
        return ""


def _format_relative_time(value):
    if not value:
        return ""
    now = timezone.localtime(timezone.now())
    local_value = timezone.localtime(value)
    seconds = max(int((now - local_value).total_seconds()), 0)
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} Min Ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} Hrs Ago"
    days = seconds // 86400
    return f"{days} Days Ago"


def _build_shell_context(request):
    current_user = request.user
    profile_name = (
        getattr(current_user, "full_name", "").strip()
        or current_user.get_full_name().strip()
        or current_user.username
    )
    name_parts = [part for part in profile_name.split() if part]
    profile_initials = "".join(part[0].upper() for part in name_parts[:2]) or profile_name[:1].upper() or "U"

    customer_results = [
        {
            "name": customer.name,
            "gender": customer.gender or "Customer",
            "customer_id": customer.customer_id,
            "image_url": _safe_file_url(customer.image),
            "initials": "".join(part[0].upper() for part in customer.name.split()[:2]) or "C",
        }
        for customer in Customer.objects.filter(status="Active").order_by("name", "id")[:4]
    ]

    recent_orders = list(
        Order.objects.exclude(status__in=["Cancelled", "Voided"])
        .order_by("-id")[:4]
    )
    order_results = [
        {
            "order_label": order.order_no or f"#{order.id:05d}",
            "type_label": "Take Away" if order.order_type == "Takeaway" else order.order_type,
            "table_name": order.table_name,
            "token_no": order.token_no,
        }
        for order in recent_orders
    ]

    kitchen_results = [
        {
            "customer_name": order.customer_name or "Walk-in Customer",
            "order_label": order.order_no or f"#{order.id:05d}",
            "service_label": "Take Away" if order.order_type == "Takeaway" else order.order_type,
        }
        for order in Order.objects.filter(status__in=["Placed", "Draft"]).order_by("-updated_at", "-id")[:4]
    ]

    notification_rows = []
    for order in Order.objects.filter(status__in=["Placed", "Draft"]).order_by("-updated_at", "-id")[:3]:
        notification_rows.append(
            {
                "icon_class": "icon-shopping-cart" if order.status == "Placed" else "icon-file-stack",
                "badge_class": "badge-soft-orange border border-orange" if order.status == "Placed" else "badge-soft-secondary border border-secondary",
                "text": f"{order.order_no or f'Order #{order.id}'} for {order.customer_name or 'Walk-in Customer'} is {order.status.lower()}.",
                "time_label": _format_relative_time(order.updated_at),
            }
        )
    for log in AuditLog.objects.select_related("actor").order_by("-created_at", "-id")[:3]:
        notification_rows.append(
            {
                "icon_class": AUDIT_ACTION_ICONS.get(log.action, "icon-info"),
                "badge_class": "badge-soft-success border border-success",
                "text": log.description or AUDIT_ACTION_LABELS.get(log.action, "Activity updated"),
                "time_label": _format_relative_time(log.created_at),
            }
        )

    return {
        "shell_profile_name": profile_name,
        "shell_profile_role": getattr(current_user, "role", "") or "User",
        "shell_profile_initials": profile_initials,
        "shell_customer_results": customer_results,
        "shell_order_results": order_results,
        "shell_kitchen_results": kitchen_results,
        "shell_notifications": notification_rows[:6],
    }


def _serialize_pos_item(item):
    variations = [
        {
            "size": variation.size,
            "price": str(variation.price),
        }
        for variation in item.variations.all()
    ]
    item_level_addons = [
        {
            "name": addon.name,
            "price": str(addon.price),
        }
        for addon in item.item_addons.all()
    ]
    category_level_addons = [
        {
            "name": addon.name,
            "price": str(addon.price),
        }
        for addon in item.category.addons.all()
        if addon.status == "Active"
    ]
    addons = item_level_addons or category_level_addons
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description or "",
        "price": str(item.price),
        "category_name": item.category.name,
        "image_url": _safe_file_url(item.image),
        "variations": variations,
        "addons": addons,
    }


def _serialize_recent_order(order, now):
    created_local = timezone.localtime(order.created_at)
    timer_started_at = order.kitchen_started_at or order.created_at
    elapsed_seconds = _get_kitchen_elapsed_seconds(order)
    elapsed_minutes = elapsed_seconds // 60
    remaining = 30 - elapsed_minutes
    badge_class = "bg-success" if remaining >= 0 else "bg-danger"
    progress_class = "bg-success" if remaining >= 0 else "bg-danger"
    progress_width = min(int((elapsed_minutes / 30) * 100), 100) if elapsed_minutes else 0

    elapsed_clock = _format_duration_clock(elapsed_seconds)

    order_label = order.order_no or f"ORD-{order.id:06d}"
    badge_icon = "icon-check-check"
    type_label = order.order_type
    if order.order_type == "Dine In":
        badge_icon = "icon-wine"
    elif order.order_type == "Takeaway":
        type_label = "Take Away"

    return {
        "id": order.id,
        "order_label": order_label,
        "customer_name": order.customer_name or "Walk-in Customer",
        "created_time": created_local.strftime("%I:%M %p"),
        "type_label": type_label,
        "badge_icon": badge_icon,
        "remaining_label": f"{remaining} Mins",
        "badge_class": badge_class,
        "progress_class": progress_class,
        "progress_width": progress_width,
        "elapsed_clock": elapsed_clock,
        "table_name": order.table_name,
        "timer_started_at_iso": timezone.localtime(timer_started_at).isoformat(),
    }


def _build_recent_orders_context(limit=18):
    now = timezone.localtime(timezone.now())
    base_qs = (
        Order.objects.exclude(status__in=["Cancelled", "Voided"])
        .order_by("-id")[:limit]
    )
    serialized = [_serialize_recent_order(order, now) for order in base_qs]
    return {
        "recent_orders_all": serialized,
        "recent_orders_dinein": [row for row in serialized if row["type_label"] == "Dine In"],
        "recent_orders_takeaway": [row for row in serialized if row["type_label"] == "Take Away"],
        "recent_orders_delivery": [row for row in serialized if row["type_label"] == "Delivery"],
        "recent_orders_table": [row for row in serialized if row["table_name"]],
    }


def _build_menu_sections_context(request):
    query = request.GET.get("q", "").strip()
    categories = list(
        Category.objects.annotate(menu_count=Count("menu_items"))
        .order_by("name")
    )
    items_qs = (
        Item.objects.select_related("category")
        .prefetch_related("variations", "item_addons", "category__addons")
        .order_by("name")
    )
    if query:
        items_qs = items_qs.filter(name__icontains=query)
    items = list(items_qs)

    category_blocks = []
    for category in categories:
        category_blocks.append(
            {
                "id": category.id,
                "name": category.name,
                "slug": f"category-{category.id}",
                "menu_count": category.menu_count,
                "image_url": _safe_file_url(category.image),
                "items": [_serialize_pos_item(item) for item in items if item.category_id == category.id],
            }
        )

    all_items = [_serialize_pos_item(item) for item in items]

    return {
        "pos_menu_categories": category_blocks,
        "pos_all_items": all_items,
        "pos_menu_query": query,
    }


def _percentage_change(current, previous):
    if previous in (None, 0):
        return 100 if current else 0
    try:
        return round(((current - previous) / previous) * 100, 1)
    except (ZeroDivisionError, TypeError):
        return 0


def _build_revenue_chart_context(base_orders, currency_symbol):
    today = timezone.localdate()

    def month_start_shift(base_date, months_back):
        month_index = (base_date.year * 12 + base_date.month - 1) - months_back
        year = month_index // 12
        month = month_index % 12 + 1
        return base_date.replace(year=year, month=month, day=1)

    weekly_points = []
    for offset in range(6, -1, -1):
        point_date = today - timedelta(days=offset)
        total = (
            base_orders.filter(created_at__date=point_date).aggregate(total=Sum("total"))["total"]
            or Decimal("0.00")
        )
        weekly_points.append({
            "label": point_date.strftime("%a"),
            "value": float(_quantize_money(total)),
        })

    monthly_points = []
    for offset in range(5, -1, -1):
        month_anchor = month_start_shift(today, offset)
        next_month = (month_anchor + timedelta(days=32)).replace(day=1)
        total = (
            base_orders.filter(created_at__date__gte=month_anchor, created_at__date__lt=next_month)
            .aggregate(total=Sum("total"))["total"]
            or Decimal("0.00")
        )
        monthly_points.append({
            "label": month_anchor.strftime("%b"),
            "value": float(_quantize_money(total)),
        })

    current_year = today.year
    yearly_points = []
    for year in range(current_year - 4, current_year + 1):
        total = (
            base_orders.filter(created_at__year=year).aggregate(total=Sum("total"))["total"]
            or Decimal("0.00")
        )
        yearly_points.append({
            "label": str(year),
            "value": float(_quantize_money(total)),
        })

    weekly_total = sum(Decimal(str(point["value"])) for point in weekly_points)
    weekly_total = _quantize_money(weekly_total)

    return {
        "default_period": "weekly",
        "summary_label": "Last 7 Days Revenue",
        "summary_total": weekly_total,
        "currency_symbol": currency_symbol,
        "periods": {
            "weekly": weekly_points,
            "monthly": monthly_points,
            "yearly": yearly_points,
        },
    }


def _get_kitchen_elapsed_seconds(order):
    start_time = order.kitchen_started_at or order.created_at
    end_time = order.kitchen_completed_at or timezone.now()
    return max(int((end_time - start_time).total_seconds()), 0)


def _format_duration_clock(total_seconds):
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _build_kitchen_order_card(order, currency_symbol):
    elapsed_seconds = _get_kitchen_elapsed_seconds(order)
    elapsed_minutes = elapsed_seconds // 60
    is_delayed = order.kitchen_status != "Completed" and elapsed_minutes > 30
    timer_started_at = order.kitchen_started_at or order.created_at

    header_class_map = {
        "New": "bg-gray",
        "In Kitchen": "bg-secondary",
        "Paused": "bg-warning",
        "Completed": "bg-success",
    }
    dot_class_map = {
        "Dine In": "success",
        "Takeaway": "",
        "Delivery": "Chicken",
    }
    progress_percent = min(int((elapsed_minutes / 30) * 100), 100) if elapsed_minutes else 5
    if order.kitchen_status == "Completed":
        progress_percent = 100

    header_class = "bg-danger" if is_delayed else header_class_map.get(order.kitchen_status, "bg-gray")
    service_label = "Take Away" if order.order_type == "Takeaway" else order.order_type
    order_label = order.order_no or f"ORD-{order.id:06d}"
    action_state = "start"
    action_label = "Play"
    action_icon = "icon-play"
    action_btn_class = "btn-light"
    if order.kitchen_status == "In Kitchen":
        action_state = "pause"
        action_label = "Pause"
        action_icon = "icon-pause"
    elif order.kitchen_status == "Paused":
        action_state = "start"
        action_label = "Play"
        action_icon = "icon-play"

    return {
        "id": order.id,
        "order_label": order_label,
        "customer_name": order.customer_name or "Walk-in Customer",
        "service_label": service_label,
        "token_no": order.token_no,
        "created_label": timezone.localtime(order.created_at).strftime("%d %b %Y, %I:%M %p"),
        "header_class": header_class,
        "status_label": "Delayed" if is_delayed else order.kitchen_status,
        "is_delayed": is_delayed,
        "delay_label": f"Delayed By {max(elapsed_minutes - 30, 0)} Mins" if is_delayed else "",
        "progress_percent": progress_percent,
        "elapsed_seconds": elapsed_seconds,
        "elapsed_clock": _format_duration_clock(elapsed_seconds),
        "timer_started_at_iso": timezone.localtime(timer_started_at).isoformat(),
        "note": (order.note or "").strip(),
        "items": list(order.items.all()),
        "dot_class": dot_class_map.get(order.order_type, ""),
        "primary_action": {
            "value": action_state,
            "label": action_label,
            "icon": action_icon,
            "button_class": action_btn_class,
        },
        "can_mark_done": order.kitchen_status != "Completed",
        "is_completed": order.kitchen_status == "Completed",
        "currency_symbol": currency_symbol,
        "subtotal_display": _quantize_money(order.subtotal),
        "tax_amount_display": _quantize_money(order.tax_amount),
        "service_charge_display": _quantize_money(order.service_charge),
        "total_display": _quantize_money(order.total),
    }


def _build_kitchen_context(request):
    search_query = request.GET.get("q", "").strip()
    Order.objects.filter(status="Placed", kitchen_status="New").update(kitchen_status="In Kitchen")
    Order.objects.filter(
        status="Placed",
        kitchen_started_at__isnull=True,
    ).exclude(kitchen_status="Completed").update(kitchen_started_at=timezone.now())
    base_qs = (
        Order.objects.exclude(status__in=["Draft", "Cancelled", "Voided"])
        .prefetch_related("items")
        .order_by(
            models.Case(
                models.When(kitchen_status="Completed", then=1),
                default=0,
                output_field=models.IntegerField(),
            ),
            "-updated_at",
            "-id",
        )
    )
    if search_query:
        base_qs = base_qs.filter(
            Q(order_no__icontains=search_query)
            | Q(customer_name__icontains=search_query)
            | Q(token_no__icontains=search_query)
            | Q(items__item_name__icontains=search_query)
        ).distinct()

    currency_symbol = StoreSetting.objects.filter(pk=1).values_list("currency_symbol", flat=True).first() or "$"
    orders = list(base_qs)
    cards = [_build_kitchen_order_card(order, currency_symbol) for order in orders]
    print_order_id = request.GET.get("print_order_id", "").strip()
    selected_print_order = None
    if print_order_id.isdigit():
        selected_print_order = next((card for card in cards if card["id"] == int(print_order_id)), None)

    delayed_count = sum(1 for card in cards if card["is_delayed"])
    context = {
        "kitchen_search_query": search_query,
        "kitchen_orders": cards,
        "kitchen_next_url": request.get_full_path(),
        "kitchen_counts": {
            "new": sum(1 for order in orders if order.kitchen_status == "New"),
            "in_kitchen": sum(1 for order in orders if order.kitchen_status == "In Kitchen"),
            "delayed": delayed_count,
            "completed": sum(1 for order in orders if order.kitchen_status == "Completed"),
        },
        "kitchen_selected_print_order": selected_print_order,
    }
    context.update(_build_shell_context(request))
    return context


def _build_dashboard_context(request):
    today = timezone.localdate()
    last_week_start = today - timedelta(days=6)
    prev_week_start = today - timedelta(days=13)
    prev_week_end = today - timedelta(days=7)

    base_orders = Order.objects.exclude(status__in=["Cancelled", "Voided"])
    recent_orders = base_orders.filter(created_at__date__gte=last_week_start)
    prev_orders = base_orders.filter(created_at__date__range=(prev_week_start, prev_week_end))

    total_orders = base_orders.count()
    total_sales = recent_orders.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    total_sales = _quantize_money(total_sales)
    avg_value = (total_sales / total_orders) if total_orders else Decimal("0.00")
    avg_value = _quantize_money(avg_value)
    reservation_count = DiningTable.objects.filter(status="Booked").count()

    change_orders = _percentage_change(recent_orders.count(), prev_orders.count())
    prev_sales_total = prev_orders.aggregate(total=Sum("total"))["total"] or Decimal("0.00")
    prev_sales_total = _quantize_money(prev_sales_total)
    change_sales = _percentage_change(float(total_sales), float(prev_sales_total))
    prev_avg = (prev_sales_total / prev_orders.count()) if prev_orders else Decimal("0.00")
    prev_avg = _quantize_money(prev_avg)
    change_avg = _percentage_change(float(avg_value), float(prev_avg))
    change_reservation = _percentage_change(
        reservation_count,
        DiningTable.objects.filter(status="Booked", updated_at__date__range=(prev_week_start, prev_week_end)).count(),
    )

    top_items = list(
        OrderItem.objects.values("item_name")
        .annotate(qty=Sum("quantity"), amount=Sum("line_total"))
        .order_by("-qty")[:6]
    )
    highlighted_item = top_items[0] if top_items else None

    recent_orders_table = list(
        base_orders.select_related("created_by").order_by("-id")[:8]
    )

    tables_available = list(DiningTable.objects.filter(status="Available").order_by("floor", "sort_order", "id")[:12])
    reservations = list(DiningTable.objects.filter(status="Booked").order_by("-updated_at", "-id")[:6])

    currency_symbol = StoreSetting.objects.filter(pk=1).values_list("currency_symbol", flat=True).first() or "$"
    revenue_chart = _build_revenue_chart_context(base_orders, currency_symbol)

    shell = _build_shell_context(request)
    shell.update({
        "dashboard_totals": {
            "orders": total_orders,
            "sales": total_sales,
            "average": avg_value,
            "reservations": reservation_count,
            "orders_change": change_orders,
            "sales_change": change_sales,
            "average_change": change_avg,
            "reservations_change": change_reservation,
            "currency_symbol": currency_symbol,
        },
        "dashboard_top_items": top_items,
        "dashboard_top_item": highlighted_item,
        "dashboard_recent_orders": recent_orders_table,
        "dashboard_tables_available": tables_available,
        "dashboard_reservations": reservations,
        "dashboard_revenue_chart": revenue_chart,
    })
    return shell


def _build_customers_context(request):
    query = request.GET.get("q", "").strip()
    page_number = request.GET.get("page", "1")
    customers_qs = Customer.objects.all().order_by("name", "id")
    if query:
        customers_qs = customers_qs.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(customers_qs, 9)
    page_obj = paginator.get_page(page_number)
    page_start = max(page_obj.number - 1, 1)
    page_end = min(page_start + 2, paginator.num_pages)
    if (page_end - page_start) < 2:
        page_start = max(page_end - 2, 1)
    page_numbers = list(range(page_start, page_end + 1))

    return {
        "customers_list": page_obj.object_list,
        "customer_query": query,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_numbers": page_numbers,
    }


def _ensure_default_roles():
    if Role.objects.exists():
        return
    Role.objects.bulk_create([Role(name=name, is_active=True) for name in DEFAULT_ROLE_NAMES])


def _ensure_role_permissions(role):
    existing_modules = set(role.permissions.values_list("module", flat=True))
    missing = [
        RolePermission(role=role, module=module_key)
        for module_key, _ in ROLE_PERMISSION_MODULES
        if module_key not in existing_modules
    ]
    if missing:
        RolePermission.objects.bulk_create(missing)


def _build_role_permissions_context():
    _ensure_default_roles()
    roles = list(Role.objects.all().prefetch_related("permissions"))
    for role in roles:
        _ensure_role_permissions(role)
    roles = list(Role.objects.all().prefetch_related("permissions"))

    roles_data = []
    for role in roles:
        permission_by_module = {perm.module: perm for perm in role.permissions.all()}
        rows = []
        for module_key, module_label in ROLE_PERMISSION_MODULES:
            perm = permission_by_module.get(module_key)
            rows.append(
                {
                    "module_key": module_key,
                    "module_label": module_label,
                    "can_view": bool(perm and perm.can_view),
                    "can_add": bool(perm and perm.can_add),
                    "can_edit": bool(perm and perm.can_edit),
                    "can_delete": bool(perm and perm.can_delete),
                    "can_export": bool(perm and perm.can_export),
                    "can_approve_void": bool(perm and perm.can_approve_void),
                }
            )

        roles_data.append(
            {
                "id": role.id,
                "name": role.name,
                "tab_id": f"role-{role.id}",
                "rows": rows,
            }
        )

    return {
        "roles_data": roles_data,
        "permission_actions": ROLE_PERMISSION_ACTIONS,
    }


def _split_name(full_name):
    value = (full_name or "").strip()
    if not value:
        return "", ""
    parts = value.split(None, 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _build_unique_username(base_text):
    raw = "".join(ch.lower() if ch.isalnum() else "_" for ch in (base_text or "user")).strip("_")
    base = raw or "user"
    candidate = base
    index = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}_{index}"
        index += 1
    return candidate[:150]


def _build_users_context(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip().lower()
    role_filter = request.GET.get("role", "").strip()
    page_number = request.GET.get("page", "1")

    users_qs = User.objects.filter(is_superuser=False).order_by("full_name", "id")
    if query:
        users_qs = users_qs.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(username__icontains=query)
            | Q(phone_number__icontains=query)
        )
    if status in {"active", "inactive"}:
        users_qs = users_qs.filter(is_active=(status == "active"))
    if role_filter:
        users_qs = users_qs.filter(role__iexact=role_filter)

    paginator = Paginator(users_qs, 10)
    page_obj = paginator.get_page(page_number)
    page_start = max(page_obj.number - 1, 1)
    page_end = min(page_start + 2, paginator.num_pages)
    if (page_end - page_start) < 2:
        page_start = max(page_end - 2, 1)
    page_numbers = list(range(page_start, page_end + 1))

    role_queryset = list(Role.objects.order_by("name"))
    roles = [role.name for role in role_queryset]
    if not roles:
        roles = [choice[0] for choice in User.ROLE]
    role_id_by_key = {role.name.lower(): role.id for role in role_queryset}

    permissions_map = {}
    role_permissions_qs = RolePermission.objects.select_related("role").all().order_by("role__name", "module")
    for perm in role_permissions_qs:
        role_key = perm.role.name.lower()
        role_rows = permissions_map.setdefault(role_key, [])
        module_label = dict(ROLE_PERMISSION_MODULES).get(perm.module, perm.module.replace("_", " ").title())
        role_rows.append(
            {
                "module_key": perm.module,
                "module_label": module_label,
                "view": perm.can_view,
                "add": perm.can_add,
                "edit": perm.can_edit,
                "delete": perm.can_delete,
                "export": perm.can_export,
                "approve_void": perm.can_approve_void,
            }
        )

    role_permission_lookup = {}
    for role_key, rows in permissions_map.items():
        for row in rows:
            role_permission_lookup[(role_key, row["module_key"])] = row

    user_ids = list(page_obj.object_list.values_list("id", flat=True))
    user_override_lookup = {}
    overrides_qs = UserPermissionOverride.objects.filter(user_id__in=user_ids).order_by("user_id", "module")
    for override in overrides_qs:
        user_override_lookup[(override.user_id, override.module)] = {
            "module_key": override.module,
            "view": override.can_view,
            "add": override.can_add,
            "edit": override.can_edit,
            "delete": override.can_delete,
            "export": override.can_export,
            "approve_void": override.can_approve_void,
            "is_override": True,
        }

    users_rows = []
    user_permissions_data = {}
    for user in page_obj.object_list:
        first_name, last_name = _split_name(user.full_name or user.username)
        role_key = (user.role or "").lower()
        effective_rows = []
        for module_key, module_label in ROLE_PERMISSION_MODULES:
            role_row = role_permission_lookup.get((role_key, module_key), {})
            override_row = user_override_lookup.get((user.id, module_key))
            source = override_row if override_row else role_row
            effective_rows.append(
                {
                    "module_key": module_key,
                    "module_label": module_label,
                    "view": bool(source.get("view")),
                    "add": bool(source.get("add")),
                    "edit": bool(source.get("edit")),
                    "delete": bool(source.get("delete")),
                    "export": bool(source.get("export")),
                    "approve_void": bool(source.get("approve_void")),
                    "is_override": bool(override_row),
                }
            )

        users_rows.append(
            {
                "id": user.id,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": user.full_name or user.username,
                "role": user.role or "-",
                "phone_number": user.phone_number or "-",
                "email": user.email,
                "status_label": "Active" if user.is_active else "Inactive",
                "status_class": "badge-soft-success" if user.is_active else "badge-soft-danger",
                "permissions_role_key": (user.role or "").lower(),
            }
        )
        user_permissions_data[str(user.id)] = {
            "user_id": user.id,
            "user_name": user.full_name or user.username,
            "role_name": user.role or "-",
            "rows": effective_rows,
        }

    return {
        "users_rows": users_rows,
        "user_query": query,
        "user_status": status,
        "user_role_filter": role_filter,
        "roles": roles,
        "role_id_by_key": role_id_by_key,
        "permissions_by_role": permissions_map,
        "user_permissions_data": user_permissions_data,
        "permission_actions": ROLE_PERMISSION_ACTIONS,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_numbers": page_numbers,
    }


def _build_audit_logs_context(request):
    query = request.GET.get("q", "").strip()
    action_filter = request.GET.get("action", "").strip()
    module_filter = request.GET.get("module", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    page_number = request.GET.get("page", "1")

    logs_qs = AuditLog.objects.select_related("actor").all()
    if query:
        logs_qs = logs_qs.filter(
            Q(description__icontains=query)
            | Q(actor_name__icontains=query)
            | Q(actor_role__icontains=query)
            | Q(target__icontains=query)
            | Q(module__icontains=query)
        )
    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)
    if module_filter:
        logs_qs = logs_qs.filter(module=module_filter)
    if date_from:
        try:
            logs_qs = logs_qs.filter(created_at__date__gte=datetime.strptime(date_from, "%Y-%m-%d").date())
        except ValueError:
            date_from = ""
    if date_to:
        try:
            logs_qs = logs_qs.filter(created_at__date__lte=datetime.strptime(date_to, "%Y-%m-%d").date())
        except ValueError:
            date_to = ""

    paginator = Paginator(logs_qs, 12)
    page_obj = paginator.get_page(page_number)
    page_start = max(page_obj.number - 1, 1)
    page_end = min(page_start + 2, paginator.num_pages)
    if (page_end - page_start) < 2:
        page_start = max(page_end - 2, 1)

    audit_logs = []
    for log in page_obj:
        audit_logs.append(
            {
                "id": log.id,
                "description": log.description,
                "actor_name": log.actor_name or "System",
                "actor_role": log.actor_role or "-",
                "target": log.target or "-",
                "module": log.module,
                "action": log.action,
                "action_label": AUDIT_ACTION_LABELS.get(log.action, log.action.replace("_", " ").title()),
                "icon": AUDIT_ACTION_ICONS.get(log.action, "icon-history"),
                "created_display": timezone.localtime(log.created_at).strftime("%d %b %Y at %I:%M %p"),
                "ip_address": log.ip_address or "-",
            }
        )

    return {
        "audit_logs": audit_logs,
        "audit_page_obj": page_obj,
        "audit_page_numbers": list(range(page_start, page_end + 1)) if paginator.num_pages else [],
        "audit_total_count": logs_qs.count(),
        "audit_action_options": [{"value": key, "label": label} for key, label in AUDIT_ACTION_LABELS.items()],
        "audit_module_options": sorted(set(AuditLog.objects.exclude(module="").values_list("module", flat=True))),
        "audit_filters": {
            "q": query,
            "action": action_filter,
            "module": module_filter,
            "date_from": date_from,
            "date_to": date_to,
        },
    }


def _build_tables_context(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    floor_filter = request.GET.get("floor", "").strip()
    page_number = request.GET.get("page", "1")

    tables_qs = DiningTable.objects.all().order_by("floor", "sort_order", "id")
    if query:
        tables_qs = tables_qs.filter(
            Q(name__icontains=query)
            | Q(floor__icontains=query)
            | Q(status__icontains=query)
        )
    if status_filter in dict(DiningTable.STATUS_CHOICES):
        tables_qs = tables_qs.filter(status=status_filter)
    if floor_filter in dict(DiningTable.FLOOR_CHOICES):
        tables_qs = tables_qs.filter(floor=floor_filter)

    paginator = Paginator(tables_qs, 16)
    page_obj = paginator.get_page(page_number)
    page_start = max(page_obj.number - 1, 1)
    page_end = min(page_start + 2, paginator.num_pages)
    if (page_end - page_start) < 2:
        page_start = max(page_end - 2, 1)

    table_rows = []
    for table in page_obj.object_list:
        table_rows.append(
            {
                "id": table.id,
                "name": table.name,
                "floor": table.floor,
                "guest_capacity": table.guest_capacity,
                "status": table.status,
                "status_class": "badge-soft-success" if table.status == "Available" else "badge-soft-danger",
                "image_name": table.image_name,
                "toggle_to": "Booked" if table.status == "Available" else "Available",
                "toggle_label": "Mark Booked" if table.status == "Available" else "Mark Available",
                "toggle_btn_class": "btn-outline-danger" if table.status == "Available" else "btn-outline-success",
                "sort_order": table.sort_order,
            }
        )

    grouped_tables = []
    for floor in [choice[0] for choice in DiningTable.FLOOR_CHOICES]:
        floor_rows = [row for row in table_rows if row["floor"] == floor]
        if floor_rows:
            grouped_tables.append({"floor": floor, "rows": floor_rows})

    context = {
        "tables_rows": table_rows,
        "tables_grouped_rows": grouped_tables,
        "tables_query": query,
        "tables_status_filter": status_filter,
        "tables_floor_filter": floor_filter,
        "tables_page_obj": page_obj,
        "tables_page_numbers": list(range(page_start, page_end + 1)) if paginator.num_pages else [],
        "tables_total_count": DiningTable.objects.count(),
        "tables_available_count": DiningTable.objects.filter(status="Available").count(),
        "tables_booked_count": DiningTable.objects.filter(status="Booked").count(),
        "tables_floor_counts": [
            {
                "floor": floor,
                "count": DiningTable.objects.filter(floor=floor).count(),
                "available_count": DiningTable.objects.filter(floor=floor, status="Available").count(),
                "booked_count": DiningTable.objects.filter(floor=floor, status="Booked").count(),
            }
            for floor in [choice[0] for choice in DiningTable.FLOOR_CHOICES]
        ],
        "table_floor_choices": [choice[0] for choice in DiningTable.FLOOR_CHOICES],
        "table_status_choices": [choice[0] for choice in DiningTable.STATUS_CHOICES],
        "table_image_choices": [
            {"value": choice[0], "label": choice[1]}
            for choice in DiningTable.IMAGE_CHOICES
        ],
    }
    context.update(_build_shell_context(request))
    return context


def _parse_report_date(value):
    value = (value or "").strip()
    if not value:
        return None
    for date_format in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    return None


def _build_earning_report_context(request):
    query = request.GET.get("q", "").strip()
    start_date_raw = request.GET.get("start_date", "").strip()
    end_date_raw = request.GET.get("end_date", "").strip()
    customer_filters = [value.strip() for value in request.GET.getlist("customer") if value.strip()]
    payment_filters = [value.strip() for value in request.GET.getlist("payment_method") if value.strip()]
    sort_by = request.GET.get("sort", "newest").strip() or "newest"
    export_format = request.GET.get("export", "").strip().lower()

    start_date = _parse_report_date(start_date_raw)
    end_date = _parse_report_date(end_date_raw)

    earnings_qs = Order.objects.filter(status="Placed")
    if query:
        earnings_qs = earnings_qs.filter(
            Q(order_no__icontains=query)
            | Q(customer_name__icontains=query)
            | Q(order_type__icontains=query)
            | Q(table_name__icontains=query)
        )
    if start_date:
        earnings_qs = earnings_qs.filter(created_at__date__gte=start_date)
    if end_date:
        earnings_qs = earnings_qs.filter(created_at__date__lte=end_date)
    if customer_filters:
        earnings_qs = earnings_qs.filter(customer_name__in=customer_filters)

    available_payment_methods = ["Not Recorded"]
    if payment_filters:
        normalized_payments = [value for value in payment_filters if value in available_payment_methods]
        if not normalized_payments:
            earnings_qs = earnings_qs.none()

    sort_label_map = {
        "newest": "Newest",
        "oldest": "Oldest",
        "ascending": "Ascending",
        "descending": "Descending",
    }
    if sort_by == "oldest":
        earnings_qs = earnings_qs.order_by("created_at", "id")
    elif sort_by == "ascending":
        earnings_qs = earnings_qs.order_by("total", "id")
    elif sort_by == "descending":
        earnings_qs = earnings_qs.order_by("-total", "-id")
    else:
        sort_by = "newest"
        earnings_qs = earnings_qs.order_by("-created_at", "-id")

    earning_rows = []
    for order in earnings_qs:
        created_local = timezone.localtime(order.created_at)
        order_label = order.order_no or f"#{order.id:05d}"
        earning_rows.append(
            {
                "earning_id": f"#ERN{order.id:04d}",
                "date_label": created_local.strftime("%d %b %Y"),
                "order_label": order_label,
                "customer_name": order.customer_name or "Walk-in Customer",
                "type_label": "Take Away" if order.order_type == "Takeaway" else order.order_type,
                "payment_method": "Not Recorded",
                "grand_total": str(order.total),
                "status_label": "Completed",
                "status_class": "badge-soft-success",
            }
        )

    if export_format in {"excel", "pdf"}:
        if export_format == "excel":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Earning ID", "Date", "Order ID", "Customer", "Type", "Payment Method", "Grand Total", "Status"])
            for row in earning_rows:
                writer.writerow([
                    row["earning_id"],
                    row["date_label"],
                    row["order_label"],
                    row["customer_name"],
                    row["type_label"],
                    row["payment_method"],
                    row["grand_total"],
                    row["status_label"],
                ])
            response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="earning_report.csv"'
            return response

        pdf_lines = [
            f"{row['earning_id']} | {row['date_label']} | {row['order_label']} | {row['customer_name']} | "
            f"{row['type_label']} | {row['payment_method']} | {row['grand_total']} | {row['status_label']}"
            for row in earning_rows
        ] or ["No earning records found for the selected filters."]
        response = HttpResponse(_build_simple_pdf(pdf_lines, title="Earning Report"), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="earning_report.pdf"'
        return response

    customer_options = sorted(
        set(
            value
            for value in Order.objects.exclude(customer_name="").values_list("customer_name", flat=True)
        )
    )

    base_query = request.GET.copy()
    if "export" in base_query:
        del base_query["export"]
    base_query_items = []
    for key, values in base_query.lists():
        for value in values:
            base_query_items.append((key, value))

    def _with_query(extra_items):
        return urlencode(base_query_items + extra_items, doseq=True)

    context = {
        "earning_rows": earning_rows,
        "earning_total_count": len(earning_rows),
        "earning_filters": {
            "q": query,
            "start_date": start_date_raw,
            "end_date": end_date_raw,
            "customers": set(customer_filters),
            "payment_methods": set(payment_filters),
            "sort": sort_by,
        },
        "earning_customer_options": customer_options,
        "earning_payment_options": available_payment_methods,
        "earning_sort_label": sort_label_map[sort_by],
        "earning_customer_label": ", ".join(customer_filters[:2]) + (" +" + str(len(customer_filters) - 2) if len(customer_filters) > 2 else "") if customer_filters else "Select",
        "earning_payment_label": ", ".join(payment_filters[:2]) + (" +" + str(len(payment_filters) - 2) if len(payment_filters) > 2 else "") if payment_filters else "Select",
        "earning_export_excel_query": _with_query([("export", "excel")]),
        "earning_export_pdf_query": _with_query([("export", "pdf")]),
        "earning_sort_queries": {
            "newest": _with_query([("sort", "newest")]),
            "oldest": _with_query([("sort", "oldest")]),
            "ascending": _with_query([("sort", "ascending")]),
            "descending": _with_query([("sort", "descending")]),
        },
    }
    context.update(_build_shell_context(request))
    return context


def _build_order_report_context(request):
    query = request.GET.get("q", "").strip()
    start_date_raw = request.GET.get("start_date", "").strip()
    end_date_raw = request.GET.get("end_date", "").strip()
    customer_filters = [value.strip() for value in request.GET.getlist("customer") if value.strip()]
    sort_by = request.GET.get("sort", "newest").strip() or "newest"
    export_format = request.GET.get("export", "").strip().lower()

    start_date = _parse_report_date(start_date_raw)
    end_date = _parse_report_date(end_date_raw)

    orders_qs = Order.objects.prefetch_related("items").all()
    if query:
        orders_qs = orders_qs.filter(
            Q(order_no__icontains=query)
            | Q(customer_name__icontains=query)
            | Q(order_type__icontains=query)
            | Q(status__icontains=query)
        )
    if start_date:
        orders_qs = orders_qs.filter(created_at__date__gte=start_date)
    if end_date:
        orders_qs = orders_qs.filter(created_at__date__lte=end_date)
    if customer_filters:
        orders_qs = orders_qs.filter(customer_name__in=customer_filters)

    sort_label_map = {
        "newest": "Newest",
        "oldest": "Oldest",
        "ascending": "Ascending",
        "descending": "Descending",
    }
    if sort_by == "oldest":
        orders_qs = orders_qs.order_by("created_at", "id")
    elif sort_by == "ascending":
        orders_qs = orders_qs.order_by("total", "id")
    elif sort_by == "descending":
        orders_qs = orders_qs.order_by("-total", "-id")
    else:
        sort_by = "newest"
        orders_qs = orders_qs.order_by("-created_at", "-id")

    order_rows = []
    for order in orders_qs:
        created_local = timezone.localtime(order.created_at)
        order_rows.append(
            {
                "order_label": order.order_no or f"#{order.id:05d}",
                "date_label": created_local.strftime("%d %b %Y"),
                "customer_name": order.customer_name or "Walk-in Customer",
                "token_no": order.token_no,
                "type_label": "Take Away" if order.order_type == "Takeaway" else order.order_type,
                "menus_count": sum(item.quantity for item in order.items.all()),
                "grand_total": str(order.total),
                "status_label": "Paid" if order.status == "Placed" else order.status,
                "status_class": "badge-soft-success" if order.status == "Placed" else "badge-soft-danger",
            }
        )

    if export_format in {"excel", "pdf"}:
        if export_format == "excel":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Order ID", "Date", "Customer", "Token No", "Type", "Menus", "Grand Total", "Status"])
            for row in order_rows:
                writer.writerow([
                    row["order_label"],
                    row["date_label"],
                    row["customer_name"],
                    row["token_no"],
                    row["type_label"],
                    row["menus_count"],
                    row["grand_total"],
                    row["status_label"],
                ])
            response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="order_report.csv"'
            return response

        pdf_lines = [
            f"{row['order_label']} | {row['date_label']} | {row['customer_name']} | Token {row['token_no']} | "
            f"{row['type_label']} | Menus {row['menus_count']} | {row['grand_total']} | {row['status_label']}"
            for row in order_rows
        ] or ["No order records found for the selected filters."]
        response = HttpResponse(_build_simple_pdf(pdf_lines, title="Order Report"), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="order_report.pdf"'
        return response

    customer_options = sorted(set(Order.objects.exclude(customer_name="").values_list("customer_name", flat=True)))
    base_query = request.GET.copy()
    if "export" in base_query:
        del base_query["export"]
    base_query_items = [(key, value) for key, values in base_query.lists() for value in values]

    def _with_query(extra_items):
        return urlencode(base_query_items + extra_items, doseq=True)

    context = {
        "order_report_rows": order_rows,
        "order_report_filters": {
            "q": query,
            "start_date": start_date_raw,
            "end_date": end_date_raw,
            "customers": set(customer_filters),
            "sort": sort_by,
        },
        "order_report_customer_options": customer_options,
        "order_report_customer_label": ", ".join(customer_filters[:2]) + (" +" + str(len(customer_filters) - 2) if len(customer_filters) > 2 else "") if customer_filters else "Select",
        "order_report_sort_label": sort_label_map[sort_by],
        "order_report_export_excel_query": _with_query([("export", "excel")]),
        "order_report_export_pdf_query": _with_query([("export", "pdf")]),
        "order_report_sort_queries": {
            "newest": _with_query([("sort", "newest")]),
            "oldest": _with_query([("sort", "oldest")]),
            "ascending": _with_query([("sort", "ascending")]),
            "descending": _with_query([("sort", "descending")]),
        },
    }
    context.update(_build_shell_context(request))
    return context


def _build_sales_report_context(request):
    start_date_raw = request.GET.get("start_date", "").strip()
    end_date_raw = request.GET.get("end_date", "").strip()
    category_filters = [value.strip() for value in request.GET.getlist("category") if value.strip()]
    sort_by = request.GET.get("sort", "newest").strip() or "newest"
    export_format = request.GET.get("export", "").strip().lower()

    start_date = _parse_report_date(start_date_raw)
    end_date = _parse_report_date(end_date_raw)

    items_by_name = {item.name: item for item in Item.objects.select_related("category")}
    orders_qs = Order.objects.filter(status="Placed").prefetch_related("items").all()
    if start_date:
        orders_qs = orders_qs.filter(created_at__date__gte=start_date)
    if end_date:
        orders_qs = orders_qs.filter(created_at__date__lte=end_date)

    sales_map = {}
    for order in orders_qs:
        created_local = timezone.localtime(order.created_at)
        for order_item in order.items.all():
            item_obj = items_by_name.get(order_item.item_name)
            category_name = item_obj.category.name if item_obj else "Uncategorized"
            if category_filters and category_name not in category_filters:
                continue
            row = sales_map.setdefault(
                category_name,
                {
                    "category_name": category_name,
                    "items_sold": 0,
                    "total_orders": set(),
                    "grand_total": Decimal("0.00"),
                    "latest_date": created_local.date(),
                },
            )
            row["items_sold"] += order_item.quantity
            row["total_orders"].add(order.id)
            row["grand_total"] += order_item.line_total
            if created_local.date() > row["latest_date"]:
                row["latest_date"] = created_local.date()

    sales_rows = []
    for idx, row in enumerate(sales_map.values(), start=1):
        sales_rows.append(
            {
                "sales_id": f"#SA{idx:04d}",
                "date_label": row["latest_date"].strftime("%d %b %Y"),
                "category_name": row["category_name"],
                "items_sold": row["items_sold"],
                "total_orders": len(row["total_orders"]),
                "grand_total": str(row["grand_total"].quantize(Decimal('0.01'))),
                "status_label": "Completed",
                "status_class": "badge-soft-success",
                "sort_date": row["latest_date"],
                "sort_total": row["grand_total"],
            }
        )

    if sort_by == "oldest":
        sales_rows.sort(key=lambda row: (row["sort_date"], row["category_name"]))
    elif sort_by == "ascending":
        sales_rows.sort(key=lambda row: (row["sort_total"], row["category_name"]))
    elif sort_by == "descending":
        sales_rows.sort(key=lambda row: (-row["sort_total"], row["category_name"]))
    else:
        sort_by = "newest"
        sales_rows.sort(key=lambda row: (row["sort_date"], row["category_name"]), reverse=True)

    for row in sales_rows:
        row.pop("sort_date", None)
        row.pop("sort_total", None)

    if export_format in {"excel", "pdf"}:
        if export_format == "excel":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Sales ID", "Date", "Category", "Items Sold", "Total Orders", "Grand Total", "Status"])
            for row in sales_rows:
                writer.writerow([row["sales_id"], row["date_label"], row["category_name"], row["items_sold"], row["total_orders"], row["grand_total"], row["status_label"]])
            response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="sales_report.csv"'
            return response

        pdf_lines = [
            f"{row['sales_id']} | {row['date_label']} | {row['category_name']} | Items {row['items_sold']} | "
            f"Orders {row['total_orders']} | {row['grand_total']} | {row['status_label']}"
            for row in sales_rows
        ] or ["No sales records found for the selected filters."]
        response = HttpResponse(_build_simple_pdf(pdf_lines, title="Sales Report"), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'
        return response

    category_options = list(Category.objects.order_by("name").values_list("name", flat=True))
    base_query = request.GET.copy()
    if "export" in base_query:
        del base_query["export"]
    base_query_items = [(key, value) for key, values in base_query.lists() for value in values]

    def _with_query(extra_items):
        return urlencode(base_query_items + extra_items, doseq=True)

    context = {
        "sales_report_rows": sales_rows,
        "sales_report_filters": {
            "start_date": start_date_raw,
            "end_date": end_date_raw,
            "categories": set(category_filters),
            "sort": sort_by,
        },
        "sales_report_category_options": category_options,
        "sales_report_category_label": ", ".join(category_filters[:2]) + (" +" + str(len(category_filters) - 2) if len(category_filters) > 2 else "") if category_filters else "Select",
        "sales_report_sort_label": {"newest": "Newest", "oldest": "Oldest", "ascending": "Ascending", "descending": "Descending"}[sort_by],
        "sales_report_export_excel_query": _with_query([("export", "excel")]),
        "sales_report_export_pdf_query": _with_query([("export", "pdf")]),
        "sales_report_sort_queries": {
            "newest": _with_query([("sort", "newest")]),
            "oldest": _with_query([("sort", "oldest")]),
            "ascending": _with_query([("sort", "ascending")]),
            "descending": _with_query([("sort", "descending")]),
        },
    }
    context.update(_build_shell_context(request))
    return context


def _build_customer_report_context(request):
    start_date_raw = request.GET.get("start_date", "").strip()
    end_date_raw = request.GET.get("end_date", "").strip()
    customer_filters = [value.strip() for value in request.GET.getlist("customer") if value.strip()]
    sort_by = request.GET.get("sort", "newest").strip() or "newest"
    export_format = request.GET.get("export", "").strip().lower()

    start_date = _parse_report_date(start_date_raw)
    end_date = _parse_report_date(end_date_raw)

    customer_lookup = {customer.name: customer for customer in Customer.objects.all()}
    orders_qs = Order.objects.filter(status="Placed").order_by("-created_at", "-id")
    if start_date:
        orders_qs = orders_qs.filter(created_at__date__gte=start_date)
    if end_date:
        orders_qs = orders_qs.filter(created_at__date__lte=end_date)
    if customer_filters:
        orders_qs = orders_qs.filter(customer_name__in=customer_filters)

    totals = defaultdict(lambda: {"orders": 0, "grand_total": Decimal("0.00"), "latest_date": None})
    for order in orders_qs:
        created_local = timezone.localtime(order.created_at)
        key = order.customer_name or "Walk-in Customer"
        totals[key]["orders"] += 1
        totals[key]["grand_total"] += order.total
        if totals[key]["latest_date"] is None or created_local.date() > totals[key]["latest_date"]:
            totals[key]["latest_date"] = created_local.date()

    customer_rows = []
    for idx, (customer_name, stats) in enumerate(totals.items(), start=1):
        customer_obj = customer_lookup.get(customer_name)
        customer_rows.append(
            {
                "customer_id": customer_obj.customer_id if customer_obj else f"#CUS{idx:04d}",
                "customer_name": customer_name,
                "image_url": _safe_file_url(customer_obj.image) if customer_obj else "",
                "initials": "".join(part[0].upper() for part in customer_name.split()[:2]) or "C",
                "total_orders": stats["orders"],
                "grand_total": str(stats["grand_total"].quantize(Decimal('0.01'))),
                "sort_date": stats["latest_date"] or datetime.now().date(),
                "sort_total": stats["grand_total"],
            }
        )

    if sort_by == "oldest":
        customer_rows.sort(key=lambda row: (row["sort_date"], row["customer_name"]))
    elif sort_by == "ascending":
        customer_rows.sort(key=lambda row: (row["sort_total"], row["customer_name"]))
    elif sort_by == "descending":
        customer_rows.sort(key=lambda row: (-row["sort_total"], row["customer_name"]))
    else:
        sort_by = "newest"
        customer_rows.sort(key=lambda row: (row["sort_date"], row["customer_name"]), reverse=True)

    for row in customer_rows:
        row.pop("sort_date", None)
        row.pop("sort_total", None)

    if export_format in {"excel", "pdf"}:
        if export_format == "excel":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Customer ID", "Customer", "Total Orders", "Grand Total"])
            for row in customer_rows:
                writer.writerow([row["customer_id"], row["customer_name"], row["total_orders"], row["grand_total"]])
            response = HttpResponse(output.getvalue(), content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="customer_report.csv"'
            return response

        pdf_lines = [
            f"{row['customer_id']} | {row['customer_name']} | Orders {row['total_orders']} | {row['grand_total']}"
            for row in customer_rows
        ] or ["No customer records found for the selected filters."]
        response = HttpResponse(_build_simple_pdf(pdf_lines, title="Customer Report"), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="customer_report.pdf"'
        return response

    customer_options = sorted(set(Order.objects.exclude(customer_name="").values_list("customer_name", flat=True)))
    base_query = request.GET.copy()
    if "export" in base_query:
        del base_query["export"]
    base_query_items = [(key, value) for key, values in base_query.lists() for value in values]

    def _with_query(extra_items):
        return urlencode(base_query_items + extra_items, doseq=True)

    context = {
        "customer_report_rows": customer_rows,
        "customer_report_filters": {
            "start_date": start_date_raw,
            "end_date": end_date_raw,
            "customers": set(customer_filters),
            "sort": sort_by,
        },
        "customer_report_customer_options": customer_options,
        "customer_report_customer_label": ", ".join(customer_filters[:2]) + (" +" + str(len(customer_filters) - 2) if len(customer_filters) > 2 else "") if customer_filters else "Select",
        "customer_report_sort_label": {"newest": "Newest", "oldest": "Oldest", "ascending": "Ascending", "descending": "Descending"}[sort_by],
        "customer_report_export_excel_query": _with_query([("export", "excel")]),
        "customer_report_export_pdf_query": _with_query([("export", "pdf")]),
        "customer_report_sort_queries": {
            "newest": _with_query([("sort", "newest")]),
            "oldest": _with_query([("sort", "oldest")]),
            "ascending": _with_query([("sort", "ascending")]),
            "descending": _with_query([("sort", "descending")]),
        },
    }
    context.update(_build_shell_context(request))
    return context


def _serialize_order(order):
    created_local = timezone.localtime(order.created_at)
    return {
        "id": order.id,
        "order_no": order.order_no,
        "token_no": order.token_no,
        "status": order.status,
        "order_type": order.order_type,
        "customer_name": order.customer_name,
        "table_name": order.table_name,
        "note": order.note,
        "subtotal": str(order.subtotal),
        "tax_rate": str(order.tax_rate),
        "tax_amount": str(order.tax_amount),
        "service_charge": str(order.service_charge),
        "total": str(order.total),
        "kitchen_status": order.kitchen_status,
        "kitchen_started_at": timezone.localtime(order.kitchen_started_at).isoformat() if order.kitchen_started_at else "",
        "kitchen_completed_at": timezone.localtime(order.kitchen_completed_at).isoformat() if order.kitchen_completed_at else "",
        "created_at": created_local.strftime("%Y-%m-%d %I:%M %p"),
        "created_at_iso": created_local.isoformat(),
        "items": [
            {
                "item_name": item.item_name,
                "unit_price": str(item.unit_price),
                "quantity": item.quantity,
                "line_total": str(item.line_total),
            }
            for item in order.items.all()
        ],
    }


def _get_latest_user_order(user):
    return (
        Order.objects.filter(created_by=user)
        .prefetch_related("items")
        .order_by("-id")
        .first()
    )


def _sync_table_status_for_order(order, status="Booked"):
    table_name = (order.table_name or "").strip()
    if not table_name:
        return
    DiningTable.objects.filter(name__iexact=table_name).update(status=status)


def _release_table_if_unused(table_name):
    normalized_name = (table_name or "").strip()
    if not normalized_name:
        return
    has_active_order = Order.objects.filter(
        table_name__iexact=normalized_name,
        status__in=["Draft", "Placed"],
    ).exists()
    if not has_active_order:
        DiningTable.objects.filter(name__iexact=normalized_name).update(status="Available")


def _extract_pos_payload(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid payload.")

    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("Cart is empty.")

    cleaned_items = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue

        name = str(raw_item.get("item_name", "")).strip()
        if not name:
            continue

        try:
            unit_price = Decimal(str(raw_item.get("unit_price", "0")))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Invalid unit price for '{name}'.")

        try:
            quantity = int(raw_item.get("quantity", 0))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid quantity for '{name}'.")

        if unit_price <= 0:
            raise ValueError(f"Unit price must be greater than 0 for '{name}'.")
        if quantity <= 0:
            raise ValueError(f"Quantity must be greater than 0 for '{name}'.")

        line_total = _quantize_money(unit_price * quantity)
        cleaned_items.append({
            "item_name": name[:150],
            "unit_price": _quantize_money(unit_price),
            "quantity": quantity,
            "line_total": line_total,
        })

    if not cleaned_items:
        raise ValueError("Cart is empty.")

    customer_name = str(payload.get("customer_name", "Walk-in Customer")).strip() or "Walk-in Customer"
    order_type = str(payload.get("order_type", "Dine In")).strip() or "Dine In"
    table_name = str(payload.get("table_name", "")).strip()
    note = str(payload.get("note", "")).strip()

    if order_type not in dict(Order.ORDER_TYPE_CHOICES):
        order_type = "Dine In"

    return {
        "items": cleaned_items,
        "customer_name": customer_name[:120],
        "order_type": order_type,
        "table_name": table_name[:60],
        "note": note,
    }


@transaction.atomic
def _create_pos_order(request, status):
    payload = _extract_pos_payload(request)
    items = payload["items"]

    subtotal = _quantize_money(sum((item["line_total"] for item in items), Decimal("0.00")))
    tax_amount = _quantize_money((subtotal * POS_TAX_RATE) / Decimal("100"))
    service_charge = POS_SERVICE_CHARGE
    total = _quantize_money(subtotal + tax_amount + service_charge)
    is_placed = status == "Placed"

    order = Order.objects.create(
        status=status,
        order_type=payload["order_type"],
        customer_name=payload["customer_name"],
        table_name=payload["table_name"],
        note=payload["note"],
        subtotal=subtotal,
        tax_rate=POS_TAX_RATE,
        tax_amount=tax_amount,
        service_charge=service_charge,
        total=total,
        kitchen_status="In Kitchen" if is_placed else "Paused",
        kitchen_started_at=timezone.now() if is_placed else None,
        created_by=request.user,
    )
    order.order_no = f"ORD-{order.id:06d}"
    order.token_no = order.id
    order.save(update_fields=["order_no", "token_no"])

    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                item_name=item["item_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                line_total=item["line_total"],
            )
            for item in items
        ]
    )
    order = Order.objects.prefetch_related("items").get(id=order.id)
    _sync_table_status_for_order(order, status="Booked")
    _log_audit_event(
        request,
        action="order_placed" if status == "Placed" else "order_drafted",
        module="POS",
        description=(
            f"Order {order.order_no} {('placed' if status == 'Placed' else 'saved as draft')} "
            f"for {order.customer_name} with total {order.total}."
        ),
        target=order.order_no,
    )
    return order


@login_required(login_url="login")
def items_view(request):
    query = request.GET.get("q", "").strip()
    page_number = request.GET.get("page", "1")
    items_queryset = Item.objects.select_related("category", "tax").prefetch_related("variations", "item_addons").all()

    if query:
        items_queryset = items_queryset.filter(name__icontains=query)

    paginator = Paginator(items_queryset, 16)
    page_obj = paginator.get_page(page_number)
    page_start = max(page_obj.number - 1, 1)
    page_end = min(page_start + 2, paginator.num_pages)
    if (page_end - page_start) < 2:
        page_start = max(page_end - 2, 1)
    page_numbers = list(range(page_start, page_end + 1))

    context = {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_numbers": page_numbers,
        "query": query,
        "all_categories": Category.objects.all(),
        "all_taxes": Tax.objects.all(),
        "addon_suggestions": list(
            Addon.objects.order_by("name").values("name", "price")
        ),
    }
    if request.GET.get("partial") == "1":
        return render(request, "partials/items_grid.html", context)
    return render(request, "items.html", context)


@login_required(login_url="login")
def item_add_view(request):
    if request.method != "POST":
        return redirect("items")

    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    category_id = request.POST.get("category_id", "").strip()
    tax_id = request.POST.get("tax_id", "").strip()
    image = request.FILES.get("image")

    if not name:
        messages.error(request, "Item name is required.")
        return redirect("items")
    if Item.objects.filter(name__iexact=name).exists():
        messages.error(request, "Item name already exists.")
        return redirect("items")

    try:
        category = Category.objects.get(id=category_id)
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Please select a valid category.")
        return redirect("items")

    try:
        tax = Tax.objects.get(id=tax_id)
    except (Tax.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Please select a valid tax.")
        return redirect("items")

    try:
        price = _parse_positive_decimal(request.POST.get("price"), "Price")
        net_price = _parse_positive_decimal(request.POST.get("net_price"), "Net price")
        variation_rows = _extract_item_child_rows(request.POST, "variation_size", "variation_price")
        addon_rows = _extract_item_child_rows(request.POST, "addon_name", "addon_price")
        _validate_unique_child_names(variation_rows, "variation")
        _validate_unique_child_names(addon_rows, "add-on")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("items")

    item = Item.objects.create(
        name=name,
        description=description,
        category=category,
        tax=tax,
        image=image,
        price=price,
        net_price=net_price,
        created_on=timezone.now().date(),
    )

    for size, variation_price in variation_rows:
        ItemVariation.objects.create(item=item, size=size, price=variation_price)
    for addon_name, addon_price in addon_rows:
        ItemAddon.objects.create(item=item, name=addon_name, price=addon_price)

    _log_audit_event(
        request,
        action="item_created",
        module="Products",
        description=f"Product '{item.name}' created in category '{item.category.name}'.",
        target=item.name,
    )
    messages.success(request, "Item added successfully.")
    return redirect("items")


@login_required(login_url="login")
def item_update_view(request):
    if request.method != "POST":
        return redirect("items")

    item_id = request.POST.get("item_id")
    try:
        item = Item.objects.get(id=item_id)
    except (Item.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Item not found.")
        return redirect("items")

    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    category_id = request.POST.get("category_id", "").strip()
    tax_id = request.POST.get("tax_id", "").strip()
    image = request.FILES.get("image")

    if not name:
        messages.error(request, "Item name is required.")
        return redirect("items")
    if Item.objects.filter(name__iexact=name).exclude(id=item.id).exists():
        messages.error(request, "Item name already exists.")
        return redirect("items")

    try:
        category = Category.objects.get(id=category_id)
    except (Category.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Please select a valid category.")
        return redirect("items")

    try:
        tax = Tax.objects.get(id=tax_id)
    except (Tax.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Please select a valid tax.")
        return redirect("items")

    try:
        price = _parse_positive_decimal(request.POST.get("price"), "Price")
        net_price = _parse_positive_decimal(request.POST.get("net_price"), "Net price")
        variation_rows = _extract_item_child_rows(request.POST, "variation_size", "variation_price")
        addon_rows = _extract_item_child_rows(request.POST, "addon_name", "addon_price")
        _validate_unique_child_names(variation_rows, "variation")
        _validate_unique_child_names(addon_rows, "add-on")
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("items")

    item.name = name
    item.description = description
    item.category = category
    item.tax = tax
    item.price = price
    item.net_price = net_price
    if image:
        item.image = image
    item.save()

    item.variations.all().delete()
    for size, variation_price in variation_rows:
        ItemVariation.objects.create(item=item, size=size, price=variation_price)

    item.item_addons.all().delete()
    for addon_name, addon_price in addon_rows:
        ItemAddon.objects.create(item=item, name=addon_name, price=addon_price)

    _log_audit_event(
        request,
        action="item_updated",
        module="Products",
        description=f"Product '{item.name}' updated in category '{item.category.name}'.",
        target=item.name,
    )
    messages.success(request, "Item updated successfully.")
    return redirect("items")


@login_required(login_url="login")
def item_delete_view(request):
    if request.method != "POST":
        return redirect("items")

    item_id = request.POST.get("item_id")
    try:
        item = Item.objects.get(id=item_id)
    except (Item.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Item not found.")
        return redirect("items")

    item_name = item.name
    item.delete()
    _log_audit_event(
        request,
        action="item_deleted",
        module="Products",
        description=f"Product '{item_name}' was deleted.",
        target=item_name,
    )
    messages.success(request, "Item deleted successfully.")
    return redirect("items")


@login_required(login_url="login")
def tables_add_view(request):
    if request.method != "POST":
        return redirect("page", page="table")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "table"})
    name = request.POST.get("name", "").strip()
    floor = request.POST.get("floor", "").strip()
    image_name = request.POST.get("image_name", "").strip()
    guest_capacity_raw = request.POST.get("guest_capacity", "").strip()
    status = request.POST.get("status", "").strip()

    if not name:
        messages.error(request, "Table name is required.")
        return redirect(next_url)
    if DiningTable.objects.filter(name__iexact=name).exists():
        messages.error(request, "Table name already exists.")
        return redirect(next_url)
    if floor not in dict(DiningTable.FLOOR_CHOICES):
        messages.error(request, "Please select a valid floor.")
        return redirect(next_url)
    if image_name not in dict(DiningTable.IMAGE_CHOICES):
        messages.error(request, "Please select a valid table image.")
        return redirect(next_url)
    if status not in dict(DiningTable.STATUS_CHOICES):
        messages.error(request, "Please select a valid status.")
        return redirect(next_url)
    try:
        guest_capacity = int(guest_capacity_raw)
        if guest_capacity <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Guest capacity must be a positive number.")
        return redirect(next_url)

    table = DiningTable.objects.create(
        name=name,
        floor=floor,
        image_name=image_name,
        guest_capacity=guest_capacity,
        status=status,
        sort_order=DiningTable.objects.filter(floor=floor).count() + 1,
    )
    _log_audit_event(
        request,
        action="table_created",
        module="Tables",
        description=f"Table '{table.name}' created on floor {table.floor}.",
        target=table.name,
    )
    messages.success(request, "Table added successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def tables_update_view(request):
    if request.method != "POST":
        return redirect("page", page="table")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "table"})
    table_id = request.POST.get("table_id", "").strip()
    try:
        table = DiningTable.objects.get(id=int(table_id))
    except (DiningTable.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Table not found.")
        return redirect(next_url)

    name = request.POST.get("name", "").strip()
    floor = request.POST.get("floor", "").strip()
    image_name = request.POST.get("image_name", "").strip()
    guest_capacity_raw = request.POST.get("guest_capacity", "").strip()
    status = request.POST.get("status", "").strip()

    if not name:
        messages.error(request, "Table name is required.")
        return redirect(next_url)
    if DiningTable.objects.filter(name__iexact=name).exclude(id=table.id).exists():
        messages.error(request, "Table name already exists.")
        return redirect(next_url)
    if floor not in dict(DiningTable.FLOOR_CHOICES):
        messages.error(request, "Please select a valid floor.")
        return redirect(next_url)
    if image_name not in dict(DiningTable.IMAGE_CHOICES):
        messages.error(request, "Please select a valid table image.")
        return redirect(next_url)
    if status not in dict(DiningTable.STATUS_CHOICES):
        messages.error(request, "Please select a valid status.")
        return redirect(next_url)
    try:
        guest_capacity = int(guest_capacity_raw)
        if guest_capacity <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Guest capacity must be a positive number.")
        return redirect(next_url)

    table.name = name
    table.floor = floor
    table.image_name = image_name
    table.guest_capacity = guest_capacity
    table.status = status
    table.save()
    _log_audit_event(
        request,
        action="table_updated",
        module="Tables",
        description=f"Table '{table.name}' updated.",
        target=table.name,
    )
    messages.success(request, "Table updated successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def tables_delete_view(request):
    if request.method != "POST":
        return redirect("page", page="table")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "table"})
    table_id = request.POST.get("table_id", "").strip()
    try:
        table = DiningTable.objects.get(id=int(table_id))
    except (DiningTable.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Table not found.")
        return redirect(next_url)

    table_name = table.name
    table.delete()
    _log_audit_event(
        request,
        action="table_deleted",
        module="Tables",
        description=f"Table '{table_name}' was deleted.",
        target=table_name,
    )
    messages.success(request, "Table deleted successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def tables_toggle_status_view(request):
    if request.method != "POST":
        return redirect("page", page="table")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "table"})
    table_id = request.POST.get("table_id", "").strip()
    try:
        table = DiningTable.objects.get(id=int(table_id))
    except (DiningTable.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Table not found.")
        return redirect(next_url)

    next_status = request.POST.get("status", "").strip()
    if next_status not in dict(DiningTable.STATUS_CHOICES):
        messages.error(request, "Invalid status.")
        return redirect(next_url)

    table.status = next_status
    table.save(update_fields=["status", "updated_at"])
    _log_audit_event(
        request,
        action="table_updated",
        module="Tables",
        description=f"Table '{table.name}' status changed to {table.status}.",
        target=table.name,
    )
    messages.success(request, f"{table.name} marked as {table.status}.")
    return redirect(next_url)


@login_required(login_url="login")
def tables_reorder_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid payload."}, status=400)

    source_floor = str(payload.get("source_floor", "")).strip()
    target_floor = str(payload.get("target_floor", "")).strip()
    source_ordered_ids = payload.get("source_ordered_ids", [])
    target_ordered_ids = payload.get("target_ordered_ids", [])
    moved_table_id = payload.get("moved_table_id")

    valid_floors = dict(DiningTable.FLOOR_CHOICES)
    if source_floor not in valid_floors or target_floor not in valid_floors:
        return JsonResponse({"ok": False, "error": "Invalid floor."}, status=400)
    if not isinstance(source_ordered_ids, list) or not isinstance(target_ordered_ids, list):
        return JsonResponse({"ok": False, "error": "Invalid order payload."}, status=400)

    source_tables = list(DiningTable.objects.filter(floor=source_floor).order_by("sort_order", "id"))
    target_tables = list(DiningTable.objects.filter(floor=target_floor).order_by("sort_order", "id"))
    source_ids_before = {table.id for table in source_tables}
    target_ids_before = {table.id for table in target_tables}
    try:
        moved_table_id = int(moved_table_id)
        source_ids_after = [int(value) for value in source_ordered_ids]
        target_ids_after = [int(value) for value in target_ordered_ids]
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid table identifiers."}, status=400)

    if source_floor == target_floor:
        if set(target_ids_after) != source_ids_before or source_ids_after:
            return JsonResponse({"ok": False, "error": "Table list mismatch."}, status=400)
    else:
        expected_source_after = source_ids_before - {moved_table_id}
        expected_target_after = target_ids_before | {moved_table_id}
        if set(source_ids_after) != expected_source_after or set(target_ids_after) != expected_target_after:
            return JsonResponse({"ok": False, "error": "Table list mismatch."}, status=400)

    table_by_id = {table.id: table for table in source_tables + target_tables}
    to_update = []
    if source_floor != target_floor:
        moved_table = table_by_id.get(moved_table_id)
        if moved_table is None:
            return JsonResponse({"ok": False, "error": "Moved table not found."}, status=400)
        moved_table.floor = target_floor

    for index, table_id in enumerate(source_ids_after, start=1):
        table = table_by_id[table_id]
        table.floor = source_floor
        table.sort_order = index
        to_update.append(table)
    for index, table_id in enumerate(target_ids_after, start=1):
        table = table_by_id[table_id]
        table.floor = target_floor
        table.sort_order = index
        to_update.append(table)
    if to_update:
        unique_updates = {table.id: table for table in to_update}
        DiningTable.objects.bulk_update(unique_updates.values(), ["floor", "sort_order"])
    _log_audit_event(
        request,
        action="table_updated",
        module="Tables",
        description=(
            f"Table layout rearranged from {source_floor} floor to {target_floor} floor."
            if source_floor != target_floor
            else f"Table order rearranged for {target_floor} floor."
        ),
        target=target_floor,
    )
    return JsonResponse({"ok": True})


@login_required(login_url="login")
def customer_add_view(request):
    if request.method != "POST":
        return redirect("page", page="pos")

    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip().lower()
    dob_raw = request.POST.get("date_of_birth", "").strip()
    gender = _valid_customer_gender(request.POST.get("gender", "").strip())
    status = _valid_customer_status(request.POST.get("status", "").strip())
    image = request.FILES.get("image")
    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "pos"})

    if not name:
        messages.error(request, "Customer name is required.")
        return redirect(next_url)
    if not phone:
        messages.error(request, "Customer phone is required.")
        return redirect(next_url)
    if not email:
        messages.error(request, "Customer email is required.")
        return redirect(next_url)
    if Customer.objects.filter(email__iexact=email).exists():
        messages.error(request, "This customer email already exists.")
        return redirect(next_url)

    date_of_birth = None
    if dob_raw:
        try:
            date_of_birth = datetime.strptime(dob_raw, "%d/%m/%Y").date()
        except ValueError:
            messages.error(request, "Date of birth format must be dd/mm/yyyy.")
            return redirect(next_url)

    Customer.objects.create(
        name=name,
        phone=phone,
        email=email,
        image=image,
        date_of_birth=date_of_birth,
        gender=gender,
        status=status,
        created_on=timezone.now().date(),
    )
    _log_audit_event(
        request,
        action="customer_created",
        module="Customers",
        description=f"Customer '{name}' created with status {status}.",
        target=name,
    )
    messages.success(request, "Customer added successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def customer_update_view(request):
    if request.method != "POST":
        return redirect("page", page="customer")

    customer_id = request.POST.get("customer_id", "").strip()
    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "customer"})

    try:
        customer = Customer.objects.get(id=int(customer_id))
    except (Customer.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Customer not found.")
        return redirect(next_url)

    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip().lower()
    dob_raw = request.POST.get("date_of_birth", "").strip()
    gender = _valid_customer_gender(request.POST.get("gender", "").strip())
    status = _valid_customer_status(request.POST.get("status", "").strip())
    image = request.FILES.get("image")
    remove_image = request.POST.get("remove_image") == "1"

    if not name:
        messages.error(request, "Customer name is required.")
        return redirect(next_url)
    if not phone:
        messages.error(request, "Customer phone is required.")
        return redirect(next_url)
    if not email:
        messages.error(request, "Customer email is required.")
        return redirect(next_url)
    if Customer.objects.filter(email__iexact=email).exclude(id=customer.id).exists():
        messages.error(request, "This customer email already exists.")
        return redirect(next_url)

    date_of_birth = None
    if dob_raw:
        try:
            date_of_birth = datetime.strptime(dob_raw, "%d/%m/%Y").date()
        except ValueError:
            messages.error(request, "Date of birth format must be dd/mm/yyyy.")
            return redirect(next_url)

    customer.name = name
    customer.phone = phone
    customer.email = email
    customer.date_of_birth = date_of_birth
    customer.gender = gender
    customer.status = status

    if remove_image:
        customer.image = None
    if image:
        customer.image = image

    customer.save()
    _log_audit_event(
        request,
        action="customer_updated",
        module="Customers",
        description=f"Customer '{customer.name}' updated.",
        target=customer.name,
    )
    messages.success(request, "Customer updated successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def users_add_view(request):
    if request.method != "POST":
        return redirect("page", page="users")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "users"})
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part).strip()
    email = request.POST.get("email", "").strip().lower()
    phone_number = request.POST.get("phone_number", "").strip()
    role_name = request.POST.get("role", "").strip() or "User"
    status_value = request.POST.get("status", "").strip().lower()
    pin_number = request.POST.get("pin_number", "").strip()
    password = request.POST.get("password", "").strip() or "123456"

    if not full_name:
        messages.error(request, "User name is required.")
        return redirect(next_url)
    if not email:
        messages.error(request, "Email is required.")
        return redirect(next_url)
    if User.objects.filter(email__iexact=email).exists():
        messages.error(request, "This email already exists.")
        return redirect(next_url)
    if not phone_number:
        messages.error(request, "Phone number is required.")
        return redirect(next_url)

    username = _build_unique_username(email.split("@")[0] if "@" in email else full_name)
    is_active = status_value != "inactive"

    try:
        created_user = User.objects.create_user(
            username=username,
            full_name=full_name,
            email=email,
            password=password,
            role=role_name,
            phone_number=phone_number,
            pin_number=pin_number or None,
            is_active=is_active,
        )
    except IntegrityError:
        messages.error(request, "Unable to create user with provided information.")
        return redirect(next_url)

    _log_audit_event(
        request,
        action="user_created",
        module="Users",
        description=f"User '{created_user.full_name or created_user.username}' created with role {created_user.role}.",
        target=created_user.username,
    )
    messages.success(request, "User added successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def users_update_view(request):
    if request.method != "POST":
        return redirect("page", page="users")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "users"})
    user_id = request.POST.get("user_id", "").strip()
    try:
        user = User.objects.get(id=int(user_id))
    except (User.DoesNotExist, TypeError, ValueError):
        messages.error(request, "User not found.")
        return redirect(next_url)

    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    full_name = " ".join(part for part in [first_name, last_name] if part).strip()
    email = request.POST.get("email", "").strip().lower()
    phone_number = request.POST.get("phone_number", "").strip()
    role_name = request.POST.get("role", "").strip() or "User"
    status_value = request.POST.get("status", "").strip().lower()
    pin_number = request.POST.get("pin_number", "").strip()
    password = request.POST.get("password", "").strip()
    confirm_password = request.POST.get("confirm_password", "").strip()

    if not full_name:
        messages.error(request, "User name is required.")
        return redirect(next_url)
    if not email:
        messages.error(request, "Email is required.")
        return redirect(next_url)
    if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
        messages.error(request, "This email already exists.")
        return redirect(next_url)
    if not phone_number:
        messages.error(request, "Phone number is required.")
        return redirect(next_url)
    if password and password != confirm_password:
        messages.error(request, "Password and confirm password do not match.")
        return redirect(next_url)

    user.full_name = full_name
    user.email = email
    user.phone_number = phone_number
    user.role = role_name
    user.pin_number = pin_number or None
    user.is_active = status_value != "inactive"
    password_changed = False
    if password:
        user.set_password(password)
        password_changed = True
    user.save()
    if password_changed and request.user.id == user.id:
        update_session_auth_hash(request, user)
    _log_audit_event(
        request,
        action="user_updated",
        module="Users",
        description=f"User '{user.full_name or user.username}' updated with role {user.role}.",
        target=user.username,
    )

    messages.success(request, "User updated successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def users_delete_view(request):
    if request.method != "POST":
        return redirect("page", page="users")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "users"})
    user_id = request.POST.get("user_id", "").strip()
    try:
        user = User.objects.get(id=int(user_id))
    except (User.DoesNotExist, TypeError, ValueError):
        messages.error(request, "User not found.")
        return redirect(next_url)

    if user.id == request.user.id:
        messages.error(request, "নিজের account delete করা যাবে না.")
        return redirect(next_url)

    deleted_username = user.username
    deleted_name = user.full_name or user.username
    user.delete()
    _log_audit_event(
        request,
        action="user_deleted",
        module="Users",
        description=f"User '{deleted_name}' was deleted.",
        target=deleted_username,
    )
    messages.success(request, "User deleted successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def users_permissions_update_view(request):
    if request.method != "POST":
        return redirect("page", page="users")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "users"})
    user_id = request.POST.get("user_id", "").strip()
    try:
        user = User.objects.get(id=int(user_id))
    except (User.DoesNotExist, TypeError, ValueError):
        messages.error(request, "User not found.")
        return redirect(next_url)

    if request.POST.get("reset_to_role") == "1":
        UserPermissionOverride.objects.filter(user=user).delete()
        _log_audit_event(
            request,
            action="user_permissions_updated",
            module="Users",
            description=f"Permission overrides reset for '{user.full_name or user.username}'.",
            target=user.username,
        )
        messages.success(request, f"Permission override cleared for {user.full_name or user.username}.")
        return redirect(next_url)

    selected_permissions = set(request.POST.getlist("perm"))
    update_rows = []
    for module_key, _ in ROLE_PERMISSION_MODULES:
        override, _ = UserPermissionOverride.objects.get_or_create(
            user=user,
            module=module_key,
        )
        for action_key, field_name, _ in ROLE_PERMISSION_ACTIONS:
            setattr(override, field_name, f"{module_key}|{action_key}" in selected_permissions)
        update_rows.append(override)

    if update_rows:
        UserPermissionOverride.objects.bulk_update(
            update_rows,
            [action[1] for action in ROLE_PERMISSION_ACTIONS],
        )
    _log_audit_event(
        request,
        action="user_permissions_updated",
        module="Users",
        description=f"Permission overrides updated for '{user.full_name or user.username}'.",
        target=user.username,
    )
    messages.success(request, f"Permission override saved for {user.full_name or user.username}.")
    return redirect(next_url)


@login_required(login_url="login")
def role_add_view(request):
    if request.method != "POST":
        return redirect("page", page="role-permission")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "role-permission"})
    role_name = request.POST.get("role_name", "").strip()
    if not role_name:
        messages.error(request, "Role name is required.")
        return redirect(next_url)

    if Role.objects.filter(name__iexact=role_name).exists():
        messages.error(request, "This role already exists.")
        return redirect(next_url)

    role = Role.objects.create(name=role_name, is_active=True, created_on=timezone.now().date())
    _ensure_role_permissions(role)
    _log_audit_event(
        request,
        action="role_created",
        module="Roles",
        description=f"Role '{role.name}' created.",
        target=role.name,
    )
    messages.success(request, "Role added successfully.")
    return redirect(next_url)


@login_required(login_url="login")
def role_permissions_update_view(request):
    if request.method != "POST":
        return redirect("page", page="role-permission")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "role-permission"})
    role_id = request.POST.get("role_id", "").strip()
    try:
        role = Role.objects.get(id=int(role_id))
    except (Role.DoesNotExist, TypeError, ValueError):
        messages.error(request, "Role not found.")
        return redirect(next_url)

    _ensure_role_permissions(role)
    selected_permissions = set(request.POST.getlist("perm"))
    to_update = []
    for permission in role.permissions.all():
        for action_key, field_name, _ in ROLE_PERMISSION_ACTIONS:
            token = f"{permission.module}|{action_key}"
            setattr(permission, field_name, token in selected_permissions)
        to_update.append(permission)

    if to_update:
        RolePermission.objects.bulk_update(
            to_update,
            [action[1] for action in ROLE_PERMISSION_ACTIONS],
        )
    _log_audit_event(
        request,
        action="role_permissions_updated",
        module="Roles",
        description=f"Permissions updated for role '{role.name}'.",
        target=role.name,
    )
    messages.success(request, f"Permissions updated for {role.name}.")
    return redirect(next_url)


@login_required(login_url="login")
def pos_order_place_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    try:
        order = _create_pos_order(request, "Placed")
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "order": _serialize_order(order)})


@login_required(login_url="login")
def pos_order_draft_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    try:
        order = _create_pos_order(request, "Draft")
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    return JsonResponse({"ok": True, "order": _serialize_order(order)})


@login_required(login_url="login")
def pos_order_cancel_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    latest_order = _get_latest_user_order(request.user)
    if latest_order is None:
        return JsonResponse({"ok": False, "error": "No order found to cancel."}, status=404)

    order_no = latest_order.order_no or f"ORD-{latest_order.id:06d}"
    table_name = latest_order.table_name
    latest_order.status = "Cancelled"
    latest_order.save(update_fields=["status", "updated_at"])
    _release_table_if_unused(table_name)
    latest_order = Order.objects.prefetch_related("items").get(id=latest_order.id)
    _log_audit_event(
        request,
        action="order_cancelled",
        module="POS",
        description=f"Order {order_no} was cancelled.",
        target=order_no,
    )
    return JsonResponse({"ok": True, "order": _serialize_order(latest_order)})


@login_required(login_url="login")
def pos_order_latest_view(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    order = _get_latest_user_order(request.user)
    if order is None:
        return JsonResponse({"ok": True, "order": None})
    return JsonResponse({"ok": True, "order": _serialize_order(order)})


@login_required(login_url="login")
def kitchen_order_action_view(request, order_id, action):
    if request.method != "POST":
        return redirect("page", page="kitchen")

    next_url = request.POST.get("next", "").strip() or reverse("page", kwargs={"page": "kitchen"})
    try:
        order = Order.objects.prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Kitchen order not found.")
        return redirect(next_url)

    if order.status in {"Draft", "Cancelled", "Voided"}:
        messages.error(request, "This order is not available in kitchen.")
        return redirect(next_url)

    update_fields = ["kitchen_status", "updated_at"]
    audit_action = ""
    audit_description = ""

    if action == "start":
        order.kitchen_status = "In Kitchen"
        if not order.kitchen_started_at:
            order.kitchen_started_at = timezone.now()
            update_fields.append("kitchen_started_at")
        audit_action = "kitchen_started"
        audit_description = f"Kitchen started order {order.order_no or f'ORD-{order.id:06d}'}."
    elif action == "pause":
        order.kitchen_status = "Paused"
        audit_action = "kitchen_paused"
        audit_description = f"Kitchen paused order {order.order_no or f'ORD-{order.id:06d}'}."
    elif action == "complete":
        order.kitchen_status = "Completed"
        if not order.kitchen_started_at:
            order.kitchen_started_at = timezone.now()
            update_fields.append("kitchen_started_at")
        order.kitchen_completed_at = timezone.now()
        update_fields.append("kitchen_completed_at")
        audit_action = "kitchen_completed"
        audit_description = f"Kitchen completed order {order.order_no or f'ORD-{order.id:06d}'}."
    else:
        messages.error(request, "Invalid kitchen action.")
        return redirect(next_url)

    order.save(update_fields=update_fields)
    _log_audit_event(
        request,
        action=audit_action,
        module="Kitchen",
        description=audit_description,
        target=order.order_no or f"ORD-{order.id:06d}",
    )
    messages.success(request, f"Kitchen action '{action}' applied for {order.order_no or f'ORD-{order.id:06d}'}.")
    return redirect(next_url)


def _build_pos_context(request):
    latest_order = _get_latest_user_order(request.user)
    print_setting, _ = PrintSetting.objects.get_or_create(pk=1)
    store_setting, _ = StoreSetting.objects.get_or_create(pk=1)
    store_logo_url = ""
    if store_setting.store_image:
        try:
            store_logo_url = store_setting.store_image.url
        except ValueError:
            store_logo_url = ""
    modal_orders_qs = (
        Order.objects.filter(created_by=request.user)
        .prefetch_related("items")
        .order_by("-id")[:120]
    )
    modal_orders = list(modal_orders_qs)
    sale_orders = [order for order in modal_orders if order.status == "Placed"]
    draft_orders = [order for order in modal_orders if order.status == "Draft"]
    pos_modes = {
        "dine_in": bool(store_setting.enable_dine_in),
        "take_away": bool(store_setting.enable_take_away),
        "delivery": bool(store_setting.enable_delivery),
        "table": bool(store_setting.enable_table),
    }
    tab_order = [
        ("order-tab1", pos_modes["dine_in"]),
        ("order-tab2", pos_modes["take_away"]),
        ("order-tab3", pos_modes["delivery"]),
        ("order-tab4", pos_modes["table"]),
    ]
    default_order_tab = "order-tab1"
    for tab_id, enabled in tab_order:
        if enabled:
            default_order_tab = tab_id
            break

    context = {
        "pos_api_urls": {
            "place": reverse("pos_order_place"),
            "draft": reverse("pos_order_draft"),
            "cancel": reverse("pos_order_cancel"),
            "latest": reverse("pos_order_latest"),
        },
        "latest_order": _serialize_order(latest_order) if latest_order else None,
        "pos_orders_all": [_serialize_order(order) for order in modal_orders],
        "pos_orders_sale": [_serialize_order(order) for order in sale_orders],
        "pos_orders_draft": [_serialize_order(order) for order in draft_orders],
        "pos_modes": pos_modes,
        "pos_default_order_tab": default_order_tab,
        "pos_print_settings": {
            "header": (print_setting.header or "").strip(),
            "footer": (print_setting.footer or "").strip(),
            "logo_url": store_logo_url,
        },
        "pos_invoice_meta": {
            "store_name": (store_setting.store_name or "").strip() or "DreamsPOS",
            "address": " ".join(
                part for part in [
                    (store_setting.address_1 or "").strip(),
                    (store_setting.address_2 or "").strip(),
                    (store_setting.city or "").strip(),
                    (store_setting.state or "").strip(),
                    (store_setting.country or "").strip(),
                    (store_setting.pincode or "").strip(),
                ] if part
            ),
            "phone": (store_setting.phone or "").strip(),
        },
        "customers": Customer.objects.filter(status="Active").order_by("name", "id"),
    }
    context.update(_build_recent_orders_context())
    context.update(_build_menu_sections_context(request))
    return context


def _currency_name_symbol(currency_code):
    return CURRENCY_META.get(currency_code)


@login_required(login_url="login")
def print_settings_view(request):
    setting, _ = PrintSetting.objects.get_or_create(pk=1)
    page_sizes = [choice[0] for choice in PrintSetting.PAGE_SIZE_CHOICES]

    if request.method == "POST":
        selected_page_size = request.POST.get("page_size", "").strip().upper()
        if selected_page_size not in page_sizes:
            messages.error(request, "Please select a valid page size.")
            return redirect("print_settings")

        setting.enable_print = "enable_print" in request.POST
        setting.show_store_details = "show_store_details" in request.POST
        setting.show_customer_details = "show_customer_details" in request.POST
        setting.page_size = selected_page_size
        setting.header = request.POST.get("header", "").strip()
        setting.footer = request.POST.get("footer", "").strip()
        setting.show_notes = "show_notes" in request.POST
        setting.print_tokens = "print_tokens" in request.POST
        setting.save()
        _log_audit_event(
            request,
            action="print_settings_updated",
            module="Print Settings",
            description=f"Print settings updated with page size {setting.page_size}.",
            target="Print Settings",
        )

        messages.success(request, "Print settings updated successfully.")
        return redirect("print_settings")

    return render(
        request,
        "print-settings.html",
        {
            "print_settings": setting,
            "print_page_sizes": page_sizes,
        },
    )


@login_required(login_url="login")
def store_settings_view(request):
    setting, _ = StoreSetting.objects.get_or_create(pk=1)

    countries = [choice[0] for choice in StoreSetting.COUNTRY_CHOICES]
    states = [choice[0] for choice in StoreSetting.STATE_CHOICES]
    cities = [choice[0] for choice in StoreSetting.CITY_CHOICES]
    currencies = [choice[0] for choice in StoreSetting.CURRENCY_CHOICES]
    currency_options = []
    for code in currencies:
        meta = _currency_name_symbol(code)
        if meta is None:
            continue
        currency_options.append(
            {
                "code": code,
                "name": meta[0],
                "symbol": meta[1],
            }
        )

    if request.method == "POST":
        store_name = request.POST.get("store_name", "").strip()
        address_1 = request.POST.get("address_1", "").strip()
        address_2 = request.POST.get("address_2", "").strip()
        country = request.POST.get("country", "").strip()
        state = request.POST.get("state", "").strip()
        city = request.POST.get("city", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        currency = request.POST.get("currency", "").strip()

        if not store_name:
            messages.error(request, "Store name is required.")
            return redirect("store_settings")
        if not address_1:
            messages.error(request, "Address 1 is required.")
            return redirect("store_settings")
        if country not in countries:
            messages.error(request, "Please select a valid country.")
            return redirect("store_settings")
        if state not in states:
            messages.error(request, "Please select a valid state.")
            return redirect("store_settings")
        if city not in cities:
            messages.error(request, "Please select a valid city.")
            return redirect("store_settings")
        if not pincode:
            messages.error(request, "Pincode is required.")
            return redirect("store_settings")
        if not email:
            messages.error(request, "Email is required.")
            return redirect("store_settings")
        if not phone:
            messages.error(request, "Phone is required.")
            return redirect("store_settings")
        if currency not in currencies:
            messages.error(request, "Please select a valid currency.")
            return redirect("store_settings")
        currency_meta = _currency_name_symbol(currency)
        if currency_meta is None:
            messages.error(request, "Currency configuration not found.")
            return redirect("store_settings")

        setting.store_name = store_name
        setting.address_1 = address_1
        setting.address_2 = address_2
        setting.country = country
        setting.state = state
        setting.city = city
        setting.pincode = pincode
        setting.email = email
        setting.phone = phone
        setting.currency = currency
        setting.currency_name = currency_meta[0]
        setting.currency_symbol = currency_meta[1]
        setting.enable_qr_menu = "enable_qr_menu" in request.POST
        setting.enable_take_away = "enable_take_away" in request.POST
        setting.enable_dine_in = "enable_dine_in" in request.POST
        setting.enable_reservation = "enable_reservation" in request.POST
        setting.enable_order_via_qr_menu = "enable_order_via_qr_menu" in request.POST
        setting.enable_delivery = "enable_delivery" in request.POST
        setting.enable_table = "enable_table" in request.POST

        if request.POST.get("remove_store_image") == "1":
            setting.store_image = None
        uploaded_image = request.FILES.get("store_image")
        if uploaded_image:
            setting.store_image = uploaded_image

        setting.save()
        _log_audit_event(
            request,
            action="store_settings_updated",
            module="Store Settings",
            description=f"Store settings updated for '{setting.store_name}'.",
            target=setting.store_name,
        )
        messages.success(request, "Store settings updated successfully.")
        return redirect("store_settings")

    return render(
        request,
        "store-settings.html",
        {
            "store_settings": setting,
            "store_countries": countries,
            "store_states": states,
            "store_cities": cities,
            "store_currencies": currencies,
            "store_currency_options": currency_options,
        },
    )


def page_view(request, page):
    public_pages = {"forgot-password", "reset-password", "email-verification", "otp"}
    if page not in public_pages and not request.user.is_authenticated:
        return redirect("login")

    template_name = f"{page}.html"
    try:
        if page in {"index", "index-2"}:
            return render(request, template_name, _build_dashboard_context(request))
        if page == "pos":
            context = _build_pos_context(request)
            if request.GET.get("partial") == "pos-left":
                return render(request, "partials/pos_left_panel.html", context)
            return render(request, template_name, context)
        if page == "kitchen":
            return render(request, template_name, _build_kitchen_context(request))
        if page == "customer":
            context = _build_customers_context(request)
            if request.GET.get("partial") == "1":
                return render(request, "partials/customers_grid.html", context)
            return render(request, template_name, context)
        if page == "table":
            return render(request, template_name, _build_tables_context(request))
        if page == "earning-report":
            earning_context = _build_earning_report_context(request)
            if isinstance(earning_context, HttpResponse):
                return earning_context
            return render(request, template_name, earning_context)
        if page == "order-report":
            order_context = _build_order_report_context(request)
            if isinstance(order_context, HttpResponse):
                return order_context
            return render(request, template_name, order_context)
        if page == "sales-report":
            sales_context = _build_sales_report_context(request)
            if isinstance(sales_context, HttpResponse):
                return sales_context
            return render(request, template_name, sales_context)
        if page == "customer-report":
            customer_context = _build_customer_report_context(request)
            if isinstance(customer_context, HttpResponse):
                return customer_context
            return render(request, template_name, customer_context)
        if page == "users":
            return render(request, template_name, _build_users_context(request))
        if page == "role-permission":
            return render(request, template_name, _build_role_permissions_context())
        if page == "audit-report":
            return render(request, template_name, _build_audit_logs_context(request))
        return render(request, template_name)
    except TemplateDoesNotExist as exc:
        raise Http404("Page not found") from exc


@login_required(login_url="login")
def dashboard_view(request):
    return render(request, "index-2.html", _build_dashboard_context(request))


@login_required(login_url="login")
def logout_view(request):
    if request.method != "POST":
        return redirect("dashboard")
    current_user = request.user
    _log_audit_event(
        request,
        action="logout",
        module="Authentication",
        description=f"User {current_user.full_name or current_user.username} signed out.",
        target=current_user.username,
        actor=current_user,
    )
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")
