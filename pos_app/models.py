from django.db import models
from django.contrib.auth.models import AbstractUser

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
