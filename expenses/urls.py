from django.urls import path
from .views import expense_list, download_expenses_pdf, manage_expenses

urlpatterns = [
    path("", expense_list, name="expense_list"),
    path("download-pdf/", download_expenses_pdf, name="download_expenses_pdf"),
    path("manage/", manage_expenses, name="manage_expenses"),

]
