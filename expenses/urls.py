from django.urls import path
from .views import expense_list, download_expenses_pdf

urlpatterns = [
    path("", expense_list, name="expense_list"),
    path("download-pdf/", download_expenses_pdf, name="download_expenses_pdf"),

]
