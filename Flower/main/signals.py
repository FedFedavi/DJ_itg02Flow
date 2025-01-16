from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Order
from main.notifications import notify_customer
from asgiref.sync import sync_to_async

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        # Запуск асинхронной функции в отдельном контексте
        sync_to_async(notify_customer)(instance.id)

