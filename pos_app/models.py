from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


POSITIVE_PRICE_VALIDATOR = MinValueValidator(Decimal("0.01"))

class User(AbstractUser):
    ROLE=[
        ('Admin','Admin'),
        ('User','User'),
    ]
    role=models.CharField(max_length=20,choices=ROLE,default='User')
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    pin_number = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username


class PrintSetting(models.Model):
    PAGE_SIZE_CHOICES = [
        ("A1", "A1"),
        ("A2", "A2"),
        ("A3", "A3"),
        ("A4", "A4"),
        ("A5", "A5"),
    ]

    enable_print = models.BooleanField(default=True)
    show_store_details = models.BooleanField(default=True)
    show_customer_details = models.BooleanField(default=True)
    page_size = models.CharField(max_length=2, choices=PAGE_SIZE_CHOICES, default="A4")
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    show_notes = models.BooleanField(default=True)
    print_tokens = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return "Print Settings"


class StoreSetting(models.Model):
    COUNTRY_CHOICES = [
        ("United States", "United States"),
        ("Canada", "Canada"),
        ("Germany", "Germany"),
        ("France", "France"),
    ]
    STATE_CHOICES = [
        ("California", "California"),
        ("New York", "New York"),
        ("Texas", "Texas"),
        ("Florida", "Florida"),
    ]
    CITY_CHOICES = [
        ("Los Angeles", "Los Angeles"),
        ("San Diego", "San Diego"),
        ("Fresno", "Fresno"),
        ("San Francisco", "San Francisco"),
    ]
    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("AED", "AED"),
        ("EUR", "EUR"),
        ("INR", "INR"),
    ]

    store_image = models.FileField(upload_to="store/", blank=True, null=True)
    store_name = models.CharField(max_length=160, default="")
    address_1 = models.CharField(max_length=255, default="")
    address_2 = models.CharField(max_length=255, blank=True, default="")
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, default="United States")
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default="California")
    city = models.CharField(max_length=80, choices=CITY_CHOICES, default="Los Angeles")
    pincode = models.CharField(max_length=20, default="")
    email = models.EmailField(default="")
    phone = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="USD")
    currency_name = models.CharField(max_length=50, default="US Dollar")
    currency_symbol = models.CharField(max_length=10, default="$")
    enable_qr_menu = models.BooleanField(default=True)
    enable_take_away = models.BooleanField(default=True)
    enable_dine_in = models.BooleanField(default=True)
    enable_reservation = models.BooleanField(default=False)
    enable_order_via_qr_menu = models.BooleanField(default=True)
    enable_delivery = models.BooleanField(default=True)
    enable_table = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return "Store Settings"


class Category(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Expired", "Expired"),
    ]

    name = models.CharField(max_length=120, unique=True)
    image = models.FileField(upload_to="categories/", blank=True, null=True)
    items_count = models.PositiveIntegerField(default=0)
    created_on = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    class Meta:
        ordering = ["-created_on", "name"]

    def __str__(self):
        return self.name


class Addon(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Expired", "Expired"),
    ]

    item = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="addons",
    )
    name = models.CharField(max_length=120)
    image = models.FileField(upload_to="addons/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-created_on", "name"]
        unique_together = ("item", "name")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="addon_price_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.item.name} - {self.name}"


class Tax(models.Model):
    TAX_TYPE_CHOICES = [
        ("Inclusive / Exclusive", "Inclusive / Exclusive"),
        ("Exclusive", "Exclusive"),
    ]

    title = models.CharField(max_length=80, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_type = models.CharField(max_length=30, choices=TAX_TYPE_CHOICES)
    created_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.rate}%)"


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="menu_items")
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, related_name="items")
    name = models.CharField(max_length=150, unique=True)
    image = models.FileField(upload_to="items/", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])
    net_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])
    created_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-created_on", "name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="item_price_gt_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(net_price__gt=0),
                name="item_net_price_gt_zero",
            ),
        ]

    def __str__(self):
        return self.name


class ItemVariation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="variations")
    size = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="item_variation_price_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.item.name} - {self.size}"


class ItemAddon(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item_addons")
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])

    class Meta:
        ordering = ["id"]
        unique_together = ("item", "name")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="item_addon_price_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.item.name} - {self.name}"


class Customer(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Disabled", "Disabled"),
    ]

    customer_id = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    image = models.FileField(upload_to="customers/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    created_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["name", "id"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.customer_id:
            self.customer_id = f"CR{self.pk:04d}"
            super().save(update_fields=["customer_id"])

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    module = models.CharField(max_length=50)
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_approve_void = models.BooleanField(default=False)

    class Meta:
        ordering = ["role_id", "module"]
        unique_together = ("role", "module")

    def __str__(self):
        return f"{self.role.name} - {self.module}"


class UserPermissionOverride(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="permission_overrides")
    module = models.CharField(max_length=50)
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_approve_void = models.BooleanField(default=False)

    class Meta:
        ordering = ["user_id", "module"]
        unique_together = ("user", "module")

    def __str__(self):
        return f"{self.user.username} - {self.module}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Placed", "Placed"),
        ("Cancelled", "Cancelled"),
        ("Voided", "Voided"),
    ]
    ORDER_TYPE_CHOICES = [
        ("Dine In", "Dine In"),
        ("Takeaway", "Takeaway"),
        ("Delivery", "Delivery"),
    ]

    order_no = models.CharField(max_length=30, unique=True, blank=True)
    token_no = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Placed")
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default="Dine In")
    customer_name = models.CharField(max_length=120, default="Walk-in Customer")
    table_name = models.CharField(max_length=60, blank=True)
    note = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("18.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    service_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.order_no or f"Order {self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[POSITIVE_PRICE_VALIDATOR])

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"
