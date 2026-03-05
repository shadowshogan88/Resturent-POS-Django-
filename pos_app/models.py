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
