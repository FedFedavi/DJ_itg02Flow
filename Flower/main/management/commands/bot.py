import os
import logging
import django
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
from django.core.management.base import BaseCommand

# Устанавливаем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Flower.settings")
django.setup()

from main.models import Order, Customer

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
API_TOKEN = "7792869223:AAHnV8lAFD0TiD2EhHYWFGc-ecLJfvoqiS4"

# Функция для получения информации о заказе
def get_order_info(order_id):
    try:
        order = Order.objects.prefetch_related('products').get(pk=order_id)
        products = order.products.all()

        product_details = "\n".join([f"{product.name} - {product.price} ₽" for product in products])
        order_info = (
            f"🛒 Заказ #{order.id}\n"
            f"📦 Продукты:\n{product_details}\n"
            f"💰 Общая стоимость: {sum([p.price for p in products])} ₽\n"
            f"📅 Дата заказа: {order.created_at.strftime('%d.%m.%Y')}\n"
            f"📍 Адрес доставки: {order.delivery_address}\n"
            f"📝 Статус: {order.get_status_display()}"
        )

        product_images = [product.image.path for product in products if product.image]
        return order_info, product_images
    except Order.DoesNotExist:
        return "Заказ не найден.", []

# Команда /register для регистрации номера телефона
def request_phone(update: Update, context: CallbackContext):
    button = KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Пожалуйста, отправьте ваш номер телефона:", reply_markup=keyboard)

# Обработка контакта пользователя
def save_telegram_id_and_check_orders(update: Update, context: CallbackContext):
    contact = update.message.contact
    if contact:
        phone_number = contact.phone_number
        telegram_id = update.message.from_user.id

        try:
            # Находим существующего клиента или создаём нового
            customer, created = Customer.objects.get_or_create(phone=phone_number)
            if not created:
                logger.info(f"Обновление Telegram ID для клиента с телефоном {phone_number}")
            customer.telegram_id = telegram_id
            customer.save()

            # Получаем заказы клиента
            orders = Order.objects.filter(customer__phone=phone_number).prefetch_related('products')

            if orders:
                update.message.reply_text("Ваш номер телефона успешно зарегистрирован! Вот ваши заказы:")
                for order in orders:
                    order_info, _ = get_order_info(order.id)
                    update.message.reply_text(order_info)
            else:
                update.message.reply_text(
                    "Ваш номер телефона успешно зарегистрирован, но заказы не найдены."
                )
        except Exception as e:
            logger.exception("Ошибка при обработке регистрации")
            update.message.reply_text("Произошла ошибка при обработке вашего запроса.")
    else:
        update.message.reply_text("Ошибка при регистрации номера телефона.")

# Команда /order для получения информации о заказе
def send_order_info(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            update.message.reply_text("Пожалуйста, укажите ID заказа после команды. Пример: /order 123")
            return

        order_id = int(args[0])
        order_info, images = get_order_info(order_id)

        update.message.reply_text(order_info)

        for image_path in images:
            if image_path:
                with open(image_path, 'rb') as image_file:
                    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file)

    except (ValueError, IndexError):
        update.message.reply_text("Пожалуйста, укажите ID заказа после команды. Пример: /order 123")
    except Exception as e:
        logger.exception(e)
        update.message.reply_text("Произошла ошибка при получении информации о заказе.")

# Основная функция для запуска бота
def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("register", request_phone))
    dispatcher.add_handler(MessageHandler(Filters.contact, save_telegram_id_and_check_orders))
    dispatcher.add_handler(CommandHandler("order", send_order_info))

    logger.info("Бот запущен!")
    updater.start_polling()
    updater.idle()

# Кастомная команда Django для запуска бота
class Command(BaseCommand):
    help = "Запуск телеграм-бота"

    def handle(self, *args, **kwargs):
        main()
