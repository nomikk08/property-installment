from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import Booking, Payment


@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    """Attach previous `is_paid` state to the instance so post_save can
    determine whether the payment transitioned from unpaid -> paid.
    """
    if instance.pk:
        try:
            old = Payment.objects.get(pk=instance.pk)
            instance._was_paid = bool(old.is_paid)
        except Payment.DoesNotExist:
            instance._was_paid = False
    else:
        instance._was_paid = False


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
    # Only create the next payment when this Payment was just marked paid
    # Use the `_was_paid` attribute set in `pre_save` to detect the transition.
    was_paid = getattr(instance, "_was_paid", False)
    if instance.is_paid and not was_paid and total_paid_count < total_months:
        # Ensure this instance is the latest payment by due_date — only the last
        # payment becoming paid should create the next installment.
        last_payment = booking.payments.order_by("-due_date").first()
        if not last_payment or last_payment.id != instance.id:
            return

        # If paid_date is not set on the last payment, fall back to due_date;
        # if still missing, use today.
        base_date = last_payment.paid_date or last_payment.due_date
        if base_date is None:
            base_date = timezone.now().date()
        next_due_date = base_date + timedelta(days=30)

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
