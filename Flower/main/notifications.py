import logging
import requests
from django.conf import settings

# Логирование
logger = logging.getLogger(__name__)

API_TOKEN = "7792869223:AAHnV8lAFD0TiD2EhHYWFGc-ecLJfvoqiS4"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"

def notify_customer_sync(order_id):
    """ Отправляет уведомление пользователю в Telegram. """
    from main.models import Order  # Локальный импорт, чтобы избежать циклической зависимости

    try:
        order = Order.objects.select_related('customer').prefetch_related('products').get(pk=order_id)

        print(f"Обрабатываем заказ #{order.id}")  # Отладка
        logger.info(f"Обрабатываем заказ #{order.id}")

        if not order.customer or not order.customer.telegram_id:
            print(f"У заказчика {order.customer} нет Telegram ID.")  # Отладка
            logger.warning(f"У заказчика {order.customer} нет Telegram ID.")
            return

        # Получаем продукты заказа
        products = order.products.all()
        if not products.exists():
            print(f"Заказ #{order.id} не содержит продуктов, но уведомление всё равно отправляем!")  # Отладка
            logger.warning(f"Заказ #{order.id} не содержит продуктов, но уведомление отправляется!")

        product_list = "\n".join([f"{p.name} - {p.price} ₽" for p in products])
        total_price = sum([p.price for p in products])

        message = (
            f"🛒 *Заказ #{order.id}*\n"
            f"📦 *Продукты:*\n{product_list or 'Нет товаров'}\n"
            f"💰 *Общая стоимость:* {total_price} ₽\n"
            f"📅 *Дата заказа:* {order.created_at.strftime('%d.%m.%Y')}\n"
            f"📍 *Адрес доставки:* {order.delivery_address or 'Не указан'}\n"
            f"📝 *Статус:* {order.get_status_display()}"
        )

        print(f"Отправка уведомления: {message}")  # Отладка
        logger.info(f"Отправка уведомления: {message}")

        response = requests.post(
            TELEGRAM_API_URL,
            json={"chat_id": order.customer.telegram_id, "text": message, "parse_mode": "Markdown"}
        )

        if response.status_code == 200:
            print(f"Уведомление отправлено пользователю {order.customer.telegram_id}")  # Отладка
            logger.info(f"Уведомление отправлено пользователю {order.customer.telegram_id}")
        else:
            print(f"Ошибка отправки: {response.status_code}, {response.text}")  # Отладка
            logger.error(f"Ошибка отправки: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")  # Отладка
        logger.exception(f"Ошибка при отправке уведомления: {e}")
