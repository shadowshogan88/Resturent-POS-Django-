from django.db import models
from django.db.models import Max
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
        ("Bangladesh", "Bangladesh"),
    ]
    STATE_CHOICES = [
        ("Dhaka", "Dhaka"),
        ("Chittagong", "Chittagong"),
        ("Khulna", "Khulna"),
        ("Rajshahi", "Rajshahi"),
        ("Barisal", "Barisal"),
        ("Sylhet", "Sylhet"),
        ("Rangpur", "Rangpur"),
        ("Mymensingh", "Mymensingh"),
        ("Comilla", "Comilla"),
        ("Gazipur", "Gazipur"),
        ("Narail", "Narail"),
        ("Jessore", "Jessore"),
        ("Feni", "Feni"),
        ("Bogra", "Bogra"),
        ("Pabna", "Pabna"),
    ]
    CITY_CHOICES = [
        ("Dhaka", "Dhaka"),
        ("Chittagong", "Chittagong"),
        ("Khulna", "Khulna"),
        ("Rajshahi", "Rajshahi"),
        ("Barisal", "Barisal"),
        ("Sylhet", "Sylhet"),
        ("Rangpur", "Rangpur"),
        ("Mymensingh", "Mymensingh"),
        ("Comilla", "Comilla"),
        ("Gazipur", "Gazipur"),
        ("Narail", "Narail"),
        ("Jessore", "Jessore"),
        ("Feni", "Feni"),
        ("Bogra", "Bogra"),
        ("Pabna", "Pabna"),
    ]
    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("AED", "AED"),
        ("EUR", "EUR"),
        ("INR", "INR"),
        ("BDT", "TK"),
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
    currency_name = models.CharField(max_length=50, default="BDT")
    currency_symbol = models.CharField(max_length=10, default="TK")
    enable_qr_menu = models.BooleanField(default=True)
    enable_take_away = models.BooleanField(default=True)
    enable_dine_in = models.BooleanField(default=True)
    enable_reservation = models.BooleanField(default=False)
    enable_order_via_qr_menu = models.BooleanField(default=True)
    enable_delivery = models.BooleanField(default=True)
    enable_table = models.BooleanField(default=True)
    enable_payment_cash = models.BooleanField(default=True)
    enable_payment_card = models.BooleanField(default=True)
    enable_payment_wallet = models.BooleanField(default=True)
    enable_payment_paypal = models.BooleanField(default=True)
    enable_payment_qr_reader = models.BooleanField(default=True)
    enable_payment_card_reader = models.BooleanField(default=True)
    enable_payment_bank = models.BooleanField(default=True)
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
        ("Inclusive", "Inclusive"),
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


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("Percentage", "Percentage"),
        ("Fixed Amount", "Fixed Amount"),
    ]

    coupon_code = models.CharField(max_length=50, unique=True)
    valid_category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="coupons", blank=True, null=True)
    applies_to_all_categories = models.BooleanField(default=False)
    valid_item = models.ForeignKey("Item", on_delete=models.PROTECT, related_name="coupons", blank=True, null=True)
    applies_to_all_items = models.BooleanField(default=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    start_date = models.DateField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_on", "coupon_code"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(discount_amount__gt=0),
                name="coupon_discount_amount_gt_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(expiry_date__gte=models.F("start_date")),
                name="coupon_expiry_on_or_after_start",
            ),
            models.CheckConstraint(
                condition=models.Q(applies_to_all_categories=True) | models.Q(valid_category__isnull=False),
                name="coupon_has_scope",
            ),
            models.CheckConstraint(
                condition=models.Q(applies_to_all_items=True) | models.Q(valid_item__isnull=False),
                name="coupon_has_item_scope",
            ),
        ]

    def __str__(self):
        return self.coupon_code


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


class AuditLog(models.Model):
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    actor_name = models.CharField(max_length=150, blank=True)
    actor_role = models.CharField(max_length=80, blank=True)
    action = models.CharField(max_length=50)
    module = models.CharField(max_length=80)
    description = models.TextField()
    target = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.action} - {self.actor_name or 'System'}"


class DiningTable(models.Model):
    FLOOR_CHOICES = [
        ("1st", "1st"),
        ("2nd", "2nd"),
        ("3rd", "3rd"),
    ]
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Booked", "Booked"),
    ]
    IMAGE_CHOICES = [
        ("tables-01.svg", "Table 1"),
        ("tables-02.svg", "Table 2"),
        ("tables-04.svg", "Table 4"),
        ("tables-05.svg", "Table 5"),
        ("tables-06.svg", "Table 6"),
        ("tables-14.svg", "Table 14"),
        ("tables-17.svg", "Table 17"),
        ("tables-18.svg", "Table 18"),
        ("tables-19.svg", "Table 19"),
    ]

    name = models.CharField(max_length=80, unique=True)
    floor = models.CharField(max_length=10, choices=FLOOR_CHOICES)
    image_name = models.CharField(max_length=20, choices=IMAGE_CHOICES, default="tables-01.svg")
    guest_capacity = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Available")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["floor", "sort_order", "id"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Placed", "Placed"),
        ("Cancelled", "Cancelled"),
        ("Voided", "Voided"),
    ]
    KITCHEN_STATUS_CHOICES = [
        ("New", "New"),
        ("In Kitchen", "In Kitchen"),
        ("Paused", "Paused"),
        ("Completed", "Completed"),
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
    kitchen_status = models.CharField(max_length=20, choices=KITCHEN_STATUS_CHOICES, default="New")
    kitchen_started_at = models.DateTimeField(blank=True, null=True)
    kitchen_completed_at = models.DateTimeField(blank=True, null=True)
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

    @classmethod
    def next_daily_token_no(cls, for_date=None):
        local_date = for_date or timezone.localdate()
        last_token = (
            cls.objects.filter(created_at__date=local_date)
            .aggregate(max_token=Max("token_no"))
            .get("max_token")
            or 0
        )
        return last_token + 1

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
