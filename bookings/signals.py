from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import Booking, Payment


@receiver(post_save, sender=Booking)
def create_first_payment(sender, instance, created, **kwargs):
    """
    When a Booking is created, create the first Payment if none exist.
    """
    if created and not instance.payments.exists():
        first_due_date = instance.start_date + timedelta(days=30)
        Payment.objects.create(
            booking=instance,
            amount=instance.monthly_installment,
            due_date=first_due_date,
        )


@receiver(post_save, sender=Payment)
def create_next_payment(sender, instance, created, **kwargs):
    """
    When a Payment is saved:
    - If it's marked as paid,
    - And the booking still has remaining months,
    - Then create the next Payment automatically.
    - If all months are paid, mark booking as completed.
    """
    booking = instance.booking
    total_paid_count = booking.payments.filter(is_paid=True).count()
    total_months = booking.installment_months

    # ✅ If this payment is paid and we still have remaining months
    if instance.is_paid and total_paid_count < total_months:
        # Find the last payment (for due date)
        last_payment = booking.payments.order_by("-due_date").first()
        next_due_date = last_payment.paid_date + timedelta(days=30)

        # Only create if there isn't already a payment with this due date
        if not booking.payments.filter(due_date=next_due_date).exists():
            Payment.objects.create(
                booking=booking,
                amount=(booking.plot_price - booking.total_paid_amount)
                / (total_months - total_paid_count),
                due_date=next_due_date,
            )

    # ✅ If all payments are paid → mark booking as completed
    if total_paid_count >= total_months:
        booking.is_completed = True
        booking.save(update_fields=["is_completed"])
