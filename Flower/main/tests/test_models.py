from django.core.exceptions import ValidationError
from django.test import TestCase
from main.models import Customer, Order, CustomUser


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser", phone_number="1234567890")
        self.customer = Customer.objects.create(name="John Doe", email="john@example.com", phone="9876543210")

    def test_order_creation(self):
        """Тест создания заказа"""
        order = Order.objects.create(user=self.user, customer=self.customer, status="PENDING")
        self.assertEqual(order.status, "PENDING")
        self.assertEqual(order.user.phone_number, "1234567890")
        self.assertEqual(order.customer.phone, "9876543210")


class CustomerModelValidationTest(TestCase):
    def test_email_unique(self):
        """Проверка уникальности email"""
        Customer.objects.create(name="Alice", email="alice@example.com")
        with self.assertRaises(ValidationError):
            customer = Customer(name="Bob", email="alice@example.com")  # Такой email уже есть
            customer.full_clean()  # Проверяем валидацию

    def test_phone_max_length(self):
        """Проверка максимальной длины телефона"""
        customer = Customer(name="Alice", email="alice@example.com", phone="1" * 20)  # 20 символов
        with self.assertRaises(ValidationError):
            customer.full_clean()  # Проверяем валидацию

class OrderModelValidationTest(TestCase):
    def test_invalid_status(self):
        """Проверка некорректного статуса"""
        user = CustomUser.objects.create(username="testuser", phone_number="1234567890")
        order = Order(user=user, status="INVALID")  # Статуса "INVALID" нет в STATUS_CHOICES
        with self.assertRaises(ValidationError):
            order.full_clean()
