from django.urls import path
from . import views

urlpatterns = [
    path("earnings/", views.earnings_page, name="earnings_page"),
    path("earnings/download-pdf/", views.download_earnings_pdf, name="download_earnings_pdf"),
    path("daily/", views.daily_report, name="daily_report"),
        path("daily/pdf/", views.download_daily_report_pdf, name="download_daily_report_pdf"),

]
