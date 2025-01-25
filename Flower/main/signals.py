from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Order, Customer
from main.notifications import notify_customer_sync  # Синхронная версия уведомлений
from django.contrib.auth.models import User

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        try:
            # Используем синхронную версию уведомлений
            notify_customer_sync(instance.id)
        except Exception as e:
            print(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")

@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    if created:
        # Синхронный запрос для создания клиента в базе
        Customer.objects.create(
            name=instance.username,
            email=instance.email if instance.email else "",
            phone="",
            telegram_id=None
        )
