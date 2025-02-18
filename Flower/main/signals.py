import time
import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from main.models import Order, Customer
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_notification_on_create_or_status_change(sender, instance, created, **kwargs):
    """ Отправляет уведомление при создании заказа или изменении его статуса. """

    if created:
        # Новый заказ
        print(f"Сигнал post_save (создание) сработал для заказа {instance.id}")
        logger.info(f"Сигнал post_save (создание) сработал для заказа {instance.id}")

        time.sleep(1)
        instance.refresh_from_db()

        if not instance.products.exists():
            print(f"Заказ #{instance.id} пока без товаров, ждем m2m_changed...")
            logger.info(f"Заказ #{instance.id} пока без товаров, ждем m2m_changed...")
            return

    else:
        # Изменение существующего заказа (например, статус)
        print(f"Сигнал post_save (изменение статуса) сработал для заказа {instance.id}")
        logger.info(f"Сигнал post_save (изменение статуса) сработал для заказа {instance.id}")

    # Отправляем уведомление в любом случае
    from main.notifications import notify_customer_sync  # Локальный импорт
    try:
        notify_customer_sync(instance.id)
    except Exception as e:
        print(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")
        logger.error(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")


@receiver(m2m_changed, sender=Order.products.through)
def send_order_notification_on_products_change(sender, instance, action, **kwargs):
    """ Отправляет уведомление при изменении списка товаров в заказе. """
    if action in ["post_add", "post_remove", "post_clear"]:
        print(f"Сигнал m2m_changed сработал для заказа {instance.id} (изменение товаров)")
        logger.info(f"Сигнал m2m_changed сработал для заказа {instance.id} (изменение товаров)")

        time.sleep(1)
        instance.refresh_from_db()

        from main.notifications import notify_customer_sync  # Локальный импорт
        try:
            notify_customer_sync(instance.id)
        except Exception as e:
            print(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")
            logger.error(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")


@receiver(post_save, sender=User)
def create_customer_for_user(sender, instance, created, **kwargs):
    """ Создает объект Customer при создании пользователя. """
    if created:
        Customer.objects.create(
            name=instance.username,
            email=instance.email if instance.email else "",
            phone="",
            telegram_id=None
        )
