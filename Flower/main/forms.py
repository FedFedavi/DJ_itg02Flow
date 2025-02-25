from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, Order, CustomUser
from django import forms
from .models import Product



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
        fields = ['products']  # Убрали 'status'
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'products': 'Продукты',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.status = 'Pending'  # Автоматически устанавливаем статус


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    phone_number = forms.CharField(required=False, label='Номер телефона')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Введите {field.label.lower()}'
            })


class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['products', 'status']
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'products': 'Продукты',
            'status': 'Статус заказа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image']  # Укажи все необходимые поля
