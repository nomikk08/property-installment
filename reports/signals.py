from django.db.models.signals import post_save
from django.dispatch import receiver
from bookings.models import Payment, Booking
from expenses.models import Expense
from .models import Transaction


@receiver(post_save, sender=Payment)
def create_credit_transaction(sender, instance, created, **kwargs):
    if instance.is_paid:
        Transaction.objects.update_or_create(
            related_payment=instance,
            defaults={
                "date": instance.paid_date or instance.due_date,
                "type": "credit",
                "amount": instance.amount,
                "description": f"Installment from {instance.booking.buyer.name}",
                "related_booking": instance.booking,
                "source": instance.source,
            },
        )


@receiver(post_save, sender=Expense)
def create_debit_transaction(sender, instance, created, **kwargs):
    if created:
        Transaction.objects.create(
            date=instance.date,
            type="debit",
            amount=instance.amount,
            description=f"{instance.title} ({instance.category.name})",
            related_expense=instance,
            source=instance.source,
        )


@receiver(post_save, sender=Booking)
def create_booking_downpayment_transaction(sender, instance, created, **kwargs):
    if created and instance.down_payment_amount > 0:
        Transaction.objects.create(
            date=instance.start_date,
            type="credit",
            amount=instance.down_payment_amount,
            description=f"Down Payment from {instance.buyer.name} ({instance.plot.title})",
            related_booking=instance,
            source=instance.source,
        )
