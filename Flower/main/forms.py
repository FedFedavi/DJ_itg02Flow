from .models import Order
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer


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

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email']


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


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите email'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'


class CustomerOrderForm(forms.ModelForm):
    """
    Форма для создания заказа, связанного с конкретным заказчиком (Customer).
    """
    class Meta:
        model = Order
        fields = ['products', 'status']
        widgets = {
            'products': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),  # Применяем класс для чекбоксов
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'products': 'Продукты',
            'status': 'Статус заказа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Применяем 'form-control' только к полям, которые не являются множественным выбором (CheckboxSelectMultiple)
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

