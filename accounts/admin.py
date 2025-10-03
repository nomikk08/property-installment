from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("is_buyer", "is_admin", "phone", "address")}),
    )
    list_display = ("username", "email", "is_buyer", "is_admin", "phone")
    search_fields = ("username", "email", "phone")
