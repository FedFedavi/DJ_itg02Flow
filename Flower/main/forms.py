from django import forms
from django.contrib.auth.models import User
from .models import Order


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return password_confirm


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['products', 'status']  # Не включаем 'user' в форму
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
            'status': forms.Select(),
        }
        labels = {
            'products': 'Продукты',
            'status': 'Статус заказа',
        }
