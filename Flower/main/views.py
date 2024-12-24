from datetime import datetime
from .models import User, Product, Order
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import RegistrationForm
from .forms import OrderForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

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
    orders = Order.objects.all()
    return render(request, 'main/order_list.html', {'orders': orders})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('index')  # Перенаправление на главную страницу
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})


def create_order(request):
    # Проверяем, аутентифицирован ли пользователь
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to create an order.")

    # Преобразуем SimpleLazyObject в User, если это необходимо
    user = request.user._wrapped if hasattr(request.user, '_wrapped') else request.user

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # Присваиваем заказ текущему пользователю
            if user:
                order.user = user  # Присваиваем заказ текущему аутентифицированному пользователю

            order.save()  # Сохраняем заказ

            form.save_m2m()  # Сохраняем связи ManyToMany, если они есть

            return redirect('main/order_list')
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})




