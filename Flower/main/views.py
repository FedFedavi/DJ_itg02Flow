from datetime import datetime
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Product
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .forms import OrderForm
from django.shortcuts import redirect, render
from .models import Customer, Order

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
            order.customer = customer  # Привязываем заказчика
            order.save()  # Сохраняем заказ
            form.save_m2m()  # Сохраняем many-to-many связи
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})

# Создание заказа для конкретного клиента
def create_order_for_customer(request):
    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            # Получаем заказчика по ID из сессии
            customer = Customer.objects.get(pk=request.session['customer_id'])

            order = form.save(commit=False)
            order.customer = customer  # Привязываем заказчика
            order.save()  # Сохраняем заказ

            return redirect('order_list')
    else:
        form = CustomerOrderForm()

    return render(request, 'create_order.html', {'form': form})
