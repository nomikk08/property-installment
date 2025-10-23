# bookings/forms.py
from django import forms
from accounts.models import Buyer
from plots.models import Plot
from .models import Booking

class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = [
            "name",
            "father_name",
            "contact_no",
            "cnic",
            "address",
            "inheritor",
            "inheritor_cnic",
            "inheritor_relation",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }

class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = [
            "title",
            "plot_type",
            "location",
            "length_ft",
            "width_ft",
            "size_sqft",
            "price",
            "price_per_sqft",
            "is_corner",
            "facing_direction",
            "block_name",
        ]

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "installment_months",
            "down_payment_amount",
            "monthly_installment",
            "commission_paid",
        ]
