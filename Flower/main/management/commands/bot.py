import os
import logging
import django
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from django.core.management.base import BaseCommand

# Устанавливаем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Flower.settings")  # Укажите ваш проект
django.setup()

from main.models import Order, Product

# Токен бота
API_TOKEN = "7792869223:AAHnV8lAFD0TiD2EhHYWFGc-ecLJfvoqiS4"

# Настраиваем бота и диспетчер
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()  # Для FSM
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Функция для получения информации о заказе
def get_order_info(order_id):
    try:
        order = Order.objects.get(pk=order_id)
        products = order.products.all()
        product_details = "\n".join(
            [f"{product.name} - {product.price} ₽" for product in products]
        )
        order_info = (
            f"🛒 Заказ #{order.id}\n"
            f"📦 Продукты:\n{product_details}\n"
            f"💰 Общая стоимость: {sum([p.price for p in products])} ₽\n"
            f"📅 Дата заказа: {order.created_at.strftime('%d.%m.%Y')}\n"
            f"📍 Адрес доставки: {order.delivery_address}\n"  # Предположим, что есть delivery_address
            f"📝 Статус: {order.get_status_display()}"
        )
        return order_info, [product.image.path for product in products if product.image]
    except Order.DoesNotExist:
        return "Заказ не найден.", []

# Команда для получения заказа
@router.message(Command("order"))
async def send_order_info(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            raise ValueError("Не указан ID заказа")

        order_id = int(args[1])  # Ожидаем "/order <id>"
        order_info, images = get_order_info(order_id)

        # Отправка информации о заказе
        await message.answer(order_info)

        # Отправка изображений
        for image_path in images:
            if image_path:
                await message.answer_photo(FSInputFile(image_path))

    except (ValueError, IndexError):
        await message.reply("Пожалуйста, укажите ID заказа после команды. Пример: /order 123")
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка при получении информации о заказе.")

# Основная асинхронная функция для запуска бота
async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

# Кастомная команда Django для запуска бота
class Command(BaseCommand):
    help = "Запуск телеграм-бота"

    def handle(self, *args, **kwargs):
        import asyncio
        asyncio.run(main())
