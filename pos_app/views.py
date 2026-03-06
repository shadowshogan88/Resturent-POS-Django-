import csv
import json
from io import StringIO
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.db import transaction
from django.db.models import Count, Q
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from .models import (
    Addon,
    Category,
    Customer,
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
                messages.error(request, "Invalid username or password.")
            else:
                login(request, user)
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

    Category.objects.create(
        name=name,
        image=image,
        items_count=items_count_value,
        status=status,
        created_on=timezone.now().date(),
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

    category.delete()
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

    Addon.objects.create(
        item=item,
        name=name,
        image=image,
        price=price,
        description=description,
        status=status,
        created_on=timezone.now().date(),
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
    addon.delete()
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
    return decimal_value


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
    elapsed_minutes = int(max((now - created_local).total_seconds(), 0) // 60)
    target_minutes = 30
    remaining = target_minutes - elapsed_minutes
    badge_class = "bg-success" if remaining >= 0 else "bg-danger"
    progress_class = "bg-success" if remaining >= 0 else "bg-danger"
    progress_width = min(int((elapsed_minutes / target_minutes) * 100), 100) if target_minutes > 0 else 0

    hours, remainder = divmod(elapsed_minutes * 60, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_clock = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"

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

    users_qs = User.objects.all().order_by("full_name", "id")
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
    return Order.objects.prefetch_related("items").get(id=order.id)


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

    item.delete()
    messages.success(request, "Item deleted successfully.")
    return redirect("items")


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
        User.objects.create_user(
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

    user.full_name = full_name
    user.email = email
    user.phone_number = phone_number
    user.role = role_name
    user.pin_number = pin_number or None
    user.is_active = status_value != "inactive"
    if password:
        user.set_password(password)
    user.save()

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

    user.delete()
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

    latest_order.status = "Cancelled"
    latest_order.save(update_fields=["status", "updated_at"])
    latest_order = Order.objects.prefetch_related("items").get(id=latest_order.id)
    return JsonResponse({"ok": True, "order": _serialize_order(latest_order)})


@login_required(login_url="login")
def pos_order_latest_view(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Method not allowed."}, status=405)

    order = _get_latest_user_order(request.user)
    if order is None:
        return JsonResponse({"ok": True, "order": None})
    return JsonResponse({"ok": True, "order": _serialize_order(order)})


def _build_pos_context(request):
    latest_order = _get_latest_user_order(request.user)
    modal_orders_qs = (
        Order.objects.filter(created_by=request.user)
        .prefetch_related("items")
        .order_by("-id")[:120]
    )
    modal_orders = list(modal_orders_qs)
    sale_orders = [order for order in modal_orders if order.status == "Placed"]
    draft_orders = [order for order in modal_orders if order.status == "Draft"]

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
        if page == "pos":
            context = _build_pos_context(request)
            if request.GET.get("partial") == "pos-left":
                return render(request, "partials/pos_left_panel.html", context)
            return render(request, template_name, context)
        if page == "customer":
            context = _build_customers_context(request)
            if request.GET.get("partial") == "1":
                return render(request, "partials/customers_grid.html", context)
            return render(request, template_name, context)
        if page == "users":
            return render(request, template_name, _build_users_context(request))
        if page == "role-permission":
            return render(request, template_name, _build_role_permissions_context())
        return render(request, template_name)
    except TemplateDoesNotExist as exc:
        raise Http404("Page not found") from exc


@login_required(login_url="login")
def dashboard_view(request):
    return render(request, "index.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")
