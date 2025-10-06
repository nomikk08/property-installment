from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    is_buyer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class Buyer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    father_name = models.CharField(max_length=100, verbose_name="Father's Name")
    contact_no = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^\d{11}$", message="Contact number must be exactly 11 digits."
            )
        ],
        verbose_name="Phone Number",
    )
    cnic = models.CharField(
        max_length=16,
        unique=True,
        validators=[
            RegexValidator(regex=r"^\d{16}$", message="CNIC must be exactly 16 digits.")
        ],
        verbose_name="CNIC Number",
    )
    address = models.TextField(verbose_name="Address")
    inheritor = models.CharField(max_length=100, verbose_name="Inheritor's Name")
    inheritor_cnic = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex=r"^\d{16}$", message="Inheritor CNIC must be exactly 16 digits."
            )
        ],
        verbose_name="Inheritor's CNIC",
    )
    inheritor_relation = models.CharField(
        max_length=50, verbose_name="Relation with Inheritor"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.name} (CNIC: {self.cnic})"
