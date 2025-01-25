from .models import Order
from .models import Customer
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


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
        fields = ['products', 'status']  # Укажите поля заказа, которые можно редактировать через форму
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
            'status': forms.Select(),
        }
        labels = {
            'products': 'Продукты',
            'status': 'Статус заказа',
        }

    def __init__(self, *args, **kwargs):
        """
        Настраивает отображение формы при ее создании.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Электронная почта', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите email'
    }))
    # phone = forms.CharField(max_length=15, label="Номер телефона", widget=forms.TextInput(attrs={
    #     'class': 'form-control',
    #     'placeholder': 'Введите номер телефона'
    # }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'Введите {field.label.lower()}'
