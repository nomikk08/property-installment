from django.contrib import admin
from .models import Transaction, PaymentSource


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("type", "amount", "related_payment", "created_at")


@admin.register(PaymentSource)
class PaymentSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "description")
    list_filter = ("is_active",)
