from datetime import datetime
from django.contrib import messages
from .forms import CustomUserCreationForm, OrderForm, CustomerOrderForm
from .models import Product, Customer, Order
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django import forms


# Главная страница
def index(request):
    context = {
        'current_year': datetime.now().year,
        'products': Product.objects.all(),
    }
    return render(request, 'main/index.html', context)


# Список пользователей
def user_list(request):
    users = User.objects.all()
    form = OrderForm()
    return render(request, 'main/user.html', {'users': users, 'form': form})


# Список товаров
def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})


# Список заказов
def order_list(request):
    orders = Order.objects.select_related('user', 'customer').all()
    return render(request, 'main/order_list.html', {'orders': orders})


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно. Теперь вы можете войти.')
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})


# Создание заказа
def create_order(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы должны быть авторизованы для создания заказа.")

    user = request.user

    # Находим или создаем связанного заказчика
    customer, created = Customer.objects.get_or_create(
        email=user.email,
        defaults={'name': user.username}
    )

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.customer = customer
            order.save()
            form.save_m2m()
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})


# Форма для заказчика
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone']


# Создание заказа для конкретного клиента
def create_order_for_customer(request, order_id=None):
    """
    Создание или редактирование заказа для конкретного клиента.
    Если order_id передан, редактируем существующий заказ.
    Если order_id не передан, создаем новый заказ.
    """
    customer_id = request.session.get('customer_id')

    # Проверка наличия заказчика в сессии
    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
    else:
        if request.method == 'POST':
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer = customer_form.save()
                request.session['customer_id'] = customer.id
                # Перенаправляем на создание заказа для нового заказчика
                return redirect('create_order_for_customer')
            else:
                return render(request, 'main/create_customer.html', {'form': customer_form})
        else:
            customer_form = CustomerForm()
            return render(request, 'main/create_customer.html', {'form': customer_form})

    # Работа с заказом
    order = get_object_or_404(Order, pk=order_id, customer=customer) if order_id else None

    if request.method == 'POST':
        form = CustomerOrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            form.save_m2m()
            return redirect('order_list')
    else:
        form = CustomerOrderForm(instance=order)

    return render(request, 'main/create_order.html', {'form': form})
