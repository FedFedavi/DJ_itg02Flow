from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Customer, Order  # Импортируем Order
from main.notifications import notify_customer_sync  # Импортируем функцию уведомлений


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Создаёт профиль для пользователя при его создании.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserProfile)
def create_customer_for_profile(sender, instance, created, **kwargs):
    """
    Создаёт клиента (Customer) для профиля, если это необходимо.
    """
    if created and instance.phone:
        Customer.objects.get_or_create(
            phone=instance.phone,
            defaults={'name': instance.user.username, 'email': instance.user.email}
        )


@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Уведомляет о создании заказа.
    """
    if created:
        try:
            notify_customer_sync(instance.id)  # Функция уведомлений
        except Exception as e:
            print(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")
