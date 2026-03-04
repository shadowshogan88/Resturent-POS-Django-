from django.contrib import admin
from .models import Category, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'phone_number', 'pin_number')
    search_fields = ('username', 'full_name', 'email') 
    list_filter = ('is_staff', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "items_count", "created_on", "status")
    search_fields = ("name",)
    list_filter = ("status", "created_on")

