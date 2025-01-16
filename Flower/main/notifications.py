from aiogram import Bot
from asgiref.sync import sync_to_async
from main.models import Order

async def notify_customer(order_id):
    order = await sync_to_async(Order.objects.select_related('user', 'customer').get)(pk=order_id)

    customer = order.customer  # Теперь это будет заранее загруженный объект
    if customer and customer.telegram_id:
        bot = Bot(token="YOUR_BOT_API_TOKEN")
        message = (
            f"Ваш заказ #{order.id} успешно создан!\n"
            f"Статус: {order.get_status_display()}\n"
            f"Общая стоимость: {sum([p.price for p in order.products.all()])} ₽"
        )
        await bot.send_message(customer.telegram_id, message)

