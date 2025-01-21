from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Order, Customer
from main.notifications import notify_customer
from asgiref.sync import async_to_sync, sync_to_async  # Добавляем sync_to_async для работы с базой данных в асинхронных функциях
from django.contrib.auth.models import User

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    if created:
        # Синхронный вызов асинхронной функции
        async_to_sync(notify_customer)(instance.id)

@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    if created:
        # Синхронный запрос для создания клиента в базе
        sync_to_async(Customer.objects.create)(
            name=instance.username,
            email=instance.email if instance.email else "",  # Избегаем ошибок с пустым email
            phone="",  # Если хотите, можно добавить поле для телефона
            telegram_id=None  # Оставляем пустым, если нет Telegram ID
        )