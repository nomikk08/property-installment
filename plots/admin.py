from django.contrib import admin
from .models import Plot, InstallmentPlan


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "size_sq_yards", "price", "status")
    list_filter = ("status", "location")
    search_fields = ("title", "location")


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "down_payment_percent", "duration_months")
    list_filter = ("duration_months",)
