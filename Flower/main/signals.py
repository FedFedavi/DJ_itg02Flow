from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Order
from main.notifications import notify_customer

@receiver(post_save, sender=Order)
async def send_order_notification(sender, instance, created, **kwargs):
    if created:
        await notify_customer(instance.id)
