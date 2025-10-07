from django.contrib import admin
from .models import Plot


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "price", "status")
    list_filter = ("status", "location")
    search_fields = ("title", "location")
