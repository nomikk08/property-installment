from django.urls import path
from . import views

urlpatterns = [
    path("", views.plot_list, name="plot_list"),
]
