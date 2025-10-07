from django.contrib import admin
from .models import Booking, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "buyer",
        "plot",
        "installment_months",
        "down_payment_amount",
        "monthly_installment",
        "start_date",
        "is_completed",
    )
    list_filter = ("is_completed", "installment_months")
    search_fields = ("buyer__username", "plot__title")
    readonly_fields = (
        "plot_price",
        "total_paid_amount",
    )
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "due_date", "paid_date", "is_paid")
    list_filter = ("is_paid", "due_date")
    search_fields = ("booking__buyer__username", "booking__plot__title")
