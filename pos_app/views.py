import csv
from io import StringIO
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from .models import Category


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
