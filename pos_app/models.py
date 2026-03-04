from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
