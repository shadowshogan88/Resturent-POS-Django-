from django.contrib import admin
from .models import Addon, Category, Item, ItemAddon, ItemVariation, Tax, User


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


@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):
    list_display = ("name", "item", "price", "status", "created_on")
    search_fields = ("name", "item__name")
    list_filter = ("status", "created_on", "item")


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("title", "rate", "tax_type", "created_on")
    search_fields = ("title",)
    list_filter = ("tax_type",)


class ItemVariationInline(admin.TabularInline):
    model = ItemVariation
    extra = 0


class ItemAddonInline(admin.TabularInline):
    model = ItemAddon
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "tax", "price", "net_price", "created_on")
    search_fields = ("name", "category__name")
    list_filter = ("category", "tax", "created_on")
    inlines = [ItemVariationInline, ItemAddonInline]

