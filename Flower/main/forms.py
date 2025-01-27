from .models import Order, Customer, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class RegistrationForm(UserCreationForm):
    """
    Форма регистрации пользователя с добавлением email.
    """
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


class CustomerForm(forms.ModelForm):
    """
    Форма для редактирования информации о клиенте.
    """
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']


class OrderForm(forms.ModelForm):
    """
    Форма для создания и редактирования заказа.
    """
    class Meta:
        model = Order
        fields = ['products', 'status']
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
            'status': forms.Select(),
        }
        labels = {
            'products': 'Продукты',
            'status': 'Статус заказа',
        }


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    """
    class Meta:
        model = UserProfile
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone
