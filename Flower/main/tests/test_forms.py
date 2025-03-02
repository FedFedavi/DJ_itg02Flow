from django.test import TestCase
from main.forms import OrderForm
from main.models import CustomUser, Customer, Order, Product


class OrderFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser", phone_number="1234567890")
        self.customer = Customer.objects.create(name="John Doe", email="john@example.com", phone="9876543210")
        self.product = Product.objects.create(name="Роза", price=100)  # Создаем товар

    def test_valid_order_form(self):
        """Форма заказа валидна при корректных данных"""
        form_data = {
            'user': self.user.id,
            'customer': self.customer.id,
            'status': 'PENDING',
            'products': [self.product.id]  # Добавляем товар
        }
        form = OrderForm(data=form_data)
        print(form.errors)  # Выведем ошибки, если тест снова не пройдет
        self.assertTrue(form.is_valid())

    def test_invalid_order_form_missing_products(self):
        """Форма заказа невалидна без товаров"""
        form_data = {
            'user': self.user.id,
            'customer': self.customer.id,
            'status': 'PENDING',
            # Поле 'products' отсутствует
        }
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('products', form.errors)  # Проверяем, что ошибка связана с отсутствием товаров
