from datetime import datetime
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Product
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .forms import OrderForm
from asgiref.sync import sync_to_async
from django.shortcuts import redirect, render
from .forms import CustomerOrderForm
from .models import Customer, Order

# Create your views here.
def index(request):
    context = {
        'current_year': datetime.now().year,
        'products': Product.objects.all(),
    }
    return render(request, 'main/index.html', context)


def user(request):
    users = User.objects.all()
    return render(request, 'main/user.html', {'users': users})


# Пример использования моделей
def user_list(request):
    users = User.objects.all()
    form = OrderForm()  # Создаём объект формы
    return render(request, 'main/user.html', {'users': users, 'form': form})  # Передаём форму в контекст


def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})

def order_list(request):
    orders = Order.objects.select_related('user', 'customer').all()
    return render(request, 'main/order_list.html', {'orders': orders})

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


# Пример обновленного представления create_order с использованием sync_to_async для работы с базой данных:
async def create_order(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы должны быть авторизованы для создания заказа.")

    user = request.user

    # Пытаемся найти связанного заказчика (обернуто в sync_to_async)
    customer, created = await sync_to_async(Customer.objects.get_or_create)(
        email=user.email,
        defaults={'name': user.username}
    )

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.customer = customer  # Привязываем заказчика
            await sync_to_async(order.save)()  # Сохранение заказа через sync_to_async
            await sync_to_async(form.save_m2m)()  # Сохранение many-to-many
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})



# Преобразуем функцию в асинхронную
async def create_order_for_customer(request):
    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            # Получаем заказчика (обернуто в sync_to_async)
            customer = await sync_to_async(Customer.objects.get)(pk=request.session['customer_id'])

            order = form.save(commit=False)
            order.customer = customer  # Привязываем заказчика
            # Сохраняем заказ через sync_to_async
            await sync_to_async(order.save)()

            return redirect('order_list')
    else:
        form = CustomerOrderForm()

    return render(request, 'create_order.html', {'form': form})



