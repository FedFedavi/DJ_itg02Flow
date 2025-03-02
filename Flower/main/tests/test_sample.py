from django.test import TestCase

class SampleTest(TestCase):
    def test_basic_math(self):
        """Простейший тест: проверяет, что 2 + 2 = 4"""
        print("Запускаем тест: test_basic_math")
        self.assertEqual(2 + 2, 4)