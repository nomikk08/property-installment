from django.contrib import admin
from .models import Booking, Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("due_date", "amount", "is_paid")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("buyer", "plot", "plan", "down_payment_amount", "monthly_installment", "start_date", "is_completed")
    list_filter = ("is_completed", "plan")
    search_fields = ("buyer__username", "plot__title")
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "due_date", "paid_date", "is_paid")
    list_filter = ("is_paid", "due_date")
    search_fields = ("booking__buyer__username", "booking__plot__title")
