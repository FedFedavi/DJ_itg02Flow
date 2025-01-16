import os
import logging
import django
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async

# Устанавливаем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Flower.settings")  # Укажите ваш проект
django.setup()

from main.models import Order, Product, Customer

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

async def get_order_info(order_id):
    try:
        # Загружаем заказ с предварительной загрузкой связанных продуктов и их изображений
        order = await sync_to_async(
            Order.objects.prefetch_related('products').get
        )(pk=order_id)

        # Получаем список продуктов
        products = order.products.all()

        # Формируем список деталей продуктов
        product_details = "\n".join(
            [f"{product.name} - {product.price} ₽" for product in products]
        )

        # Формируем текст информации о заказе
        order_info = (
            f"🛒 Заказ #{order.id}\n"
            f"📦 Продукты:\n{product_details}\n"
            f"💰 Общая стоимость: {sum([p.price for p in products])} ₽\n"
            f"📅 Дата заказа: {order.created_at.strftime('%d.%m.%Y')}\n"
            f"📍 Адрес доставки: {order.delivery_address}\n"
            f"📝 Статус: {order.get_status_display()}"
        )

        # Формируем список путей к изображениям продуктов
        product_images = [
            product.image.path for product in products if product.image
        ]

        return order_info, product_images
    except Order.DoesNotExist:
        return "Заказ не найден.", []


# Команда для регистрации номера телефона
@router.message(Command("register"))
async def request_phone(message: types.Message):
    # Создаем кнопку с запросом номера телефона
    button = KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button]],  # Обратите внимание на этот параметр
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Пожалуйста, отправьте ваш номер телефона, нажав кнопку ниже:",
        reply_markup=keyboard,
    )

# Обработка номера телефона
@router.message(lambda message: message.contact)
async def save_telegram_id_and_check_orders(message: types.Message):
    contact = message.contact
    if contact:
        phone_number = contact.phone_number
        telegram_id = message.from_user.id

        # Сохранение пользователя в базу данных
        customer, created = await sync_to_async(Customer.objects.get_or_create)(phone=phone_number)
        customer.telegram_id = telegram_id
        await sync_to_async(customer.save)()

        # Поиск заказов, связанных с этим номером телефона
        orders = await sync_to_async(list)(
            Order.objects.filter(customer__phone=phone_number).select_related("customer").prefetch_related("products")
        )

        if orders:
            # Если есть заказы, отправляем информацию о каждом заказе
            await message.answer("Ваш номер телефона успешно зарегистрирован! Вот ваши заказы:")
            for order in orders:
                products = await sync_to_async(list)(order.products.all())
                product_details = "\n".join(
                    [f"{product.name} - {product.price} ₽" for product in products]
                )
                order_info = (
                    f"🛒 Заказ #{order.id}\n"
                    f"📦 Продукты:\n{product_details}\n"
                    f"💰 Общая стоимость: {sum([p.price for p in products])} ₽\n"
                    f"📅 Дата заказа: {order.created_at.strftime('%d.%m.%Y')}\n"
                    f"📍 Адрес доставки: {order.delivery_address}\n"
                    f"📝 Статус: {order.get_status_display()}"
                )
                await message.answer(order_info)
        else:
            # Если заказов нет
            await message.answer(
                "Ваш номер телефона успешно зарегистрирован, но заказы, связанные с этим номером, не найдены."
            )
    else:
        await message.answer("Ошибка при регистрации номера телефона.")

# Команда для получения заказа
@router.message(Command("order"))
async def send_order_info(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            raise ValueError("Не указан ID заказа")

        order_id = int(args[1])  # Ожидаем "/order <id>"
        order_info, images = await get_order_info(order_id)

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
