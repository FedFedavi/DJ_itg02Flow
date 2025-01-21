from aiogram import Bot
from asgiref.sync import sync_to_async
from main.models import Order

# Асинхронная функция для отправки уведомления
async def notify_customer(order_id):
    order = await sync_to_async(Order.objects.select_related('user', 'customer').get)(pk=order_id)

    # Используем sync_to_async для асинхронного выполнения запроса
    products = await sync_to_async(lambda: order.products.all())()  # Ожидаем получения продуктов

    customer = order.customer  # Это будет заранее загруженный объект
    if customer and customer.telegram_id:
        bot = Bot(token="7792869223:AAHnV8lAFD0TiD2EhHYWFGc-ecLJfvoqiS4")
        # Формируем сообщение
        message = (
            f"Ваш заказ #{order.id} успешно создан!\n"
            f"Статус: {order.get_status_display()}\n"
            f"Общая стоимость: {sum([p.price for p in products])} ₽"
        )
        await bot.send_message(customer.telegram_id, message)
