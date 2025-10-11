from django.urls import path
from .views import earnings_page, download_earnings_pdf

urlpatterns = [
    path("earnings/", earnings_page, name="earnings_page"),
    path("earnings/download-pdf/", download_earnings_pdf, name="download_earnings_pdf"),
]
