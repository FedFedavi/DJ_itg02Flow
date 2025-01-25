import logging
import requests
from django.conf import settings
from main.models import Order

# Настройка логирования
logger = logging.getLogger(__name__)

API_TOKEN = "7792869223:AAHnV8lAFD0TiD2EhHYWFGc-ecLJfvoqiS4"

# URL для отправки сообщений через Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"

def notify_customer_sync(order_id):
    try:
        # Получаем заказ из базы данных
        order = Order.objects.select_related('customer').get(pk=order_id)

        # Получаем связанные продукты
        products = order.products.all()

        # Проверяем, есть ли у заказчика Telegram ID
        customer = order.customer
        if customer and customer.telegram_id:
            # Формируем сообщение
            message = (
                f"Ваш заказ #{order.id} успешно создан!\n"
                f"Статус: {order.get_status_display()}\n"
                f"Общая стоимость: {sum([p.price for p in products])} ₽"
            )

            # Отправляем сообщение через Telegram API
            response = requests.post(
                TELEGRAM_API_URL,
                json={
                    "chat_id": customer.telegram_id,
                    "text": message,
                }
            )

            # Проверяем успешность запроса
            if response.status_code == 200:
                logger.info(f"Уведомление успешно отправлено пользователю {customer.telegram_id}")
            else:
                logger.error(f"Ошибка отправки уведомления: {response.status_code}, {response.text}")
        else:
            logger.warning(f"У заказчика {order.customer.id} не указан Telegram ID.")
    except Order.DoesNotExist:
        logger.error(f"Заказ с ID {order_id} не найден.")
    except Exception as e:
        logger.exception(f"Произошла ошибка: {e}")
