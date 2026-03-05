import csv
from io import StringIO
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from .models import Addon, Category, Item, ItemAddon, ItemVariation, Tax


User = get_user_model()


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

    if variation_rows:
        item.variations.all().delete()
        for size, variation_price in variation_rows:
            ItemVariation.objects.create(item=item, size=size, price=variation_price)

    if addon_rows:
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


def page_view(request, page):
    public_pages = {"forgot-password", "reset-password", "email-verification", "otp"}
    if page not in public_pages and not request.user.is_authenticated:
        return redirect("login")

    template_name = f"{page}.html"
    try:
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
