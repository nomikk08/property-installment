from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Buyer


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("is_buyer", "is_admin", "phone", "address")}),
    )
    list_display = ("username", "email", "is_buyer", "is_admin", "phone")
    search_fields = ("username", "email", "phone")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "father_name",
        "contact_no",
        "cnic",
        "inheritor",
        "created_at",
    )
    search_fields = ("name", "cnic", "contact_no", "inheritor")
    list_filter = ("inheritor_relation",)
