from datetime import datetime
from django.contrib import messages
from .forms import CustomUserCreationForm, OrderForm, CustomerOrderForm
from django import forms
from .models import CustomUser as User
from django.contrib.auth import login, authenticate
from django.db.models import Q
from .forms import ProductForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Order, Product, Customer



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
# Список заказов (показываем только свои)
def order_list(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы должны быть авторизованы для просмотра заказов.")

    user = request.user

    # Администратор видит все заказы
    if user.is_superuser:
        orders = Order.objects.select_related('user', 'customer').all()
    else:
        # Показываем заказы, где пользователь — автор заказа (user) или заказчик (customer)
        orders = Order.objects.filter(Q(user=user) | Q(customer__email=user.email)).distinct()

    return render(request, 'main/order_list.html', {'orders': orders})



# Регистрация пользователя

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход
            messages.success(request, 'Регистрация прошла успешно! Вы вошли в систему.')
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

    # Находим или создаем заказчика
    customer, created = Customer.objects.get_or_create(
        email=user.email,
        defaults={'name': user.username, 'phone': user.phone_number}
    )

    order = None
    if 'order_id' in request.GET:
        order = get_object_or_404(Order, id=request.GET['order_id'])

    if request.method == 'POST':
        print("POST Data:", request.POST)  # Отладка
        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.customer = customer

            if not order.id:
                order.status = 'PENDING'  # Исправляем на верхний регистр

            order.save()

            # Обновляем продукты
            selected_products = request.POST.getlist('products')  # Получаем список ID
            order.products.set(selected_products)  # Привязываем продукты к заказу
            print("Selected Products:", selected_products)  # Отладка

            return redirect('order_list')
        else:
            print("Form Errors:", form.errors)  # Отладка ошибок

    else:
        form = OrderForm(instance=order)

    # Передаем выбранные продукты
    products_with_images = Product.objects.all()
    selected_products = order.products.values_list('id', flat=True) if order else []

    return render(request, 'main/create_order.html', {
        'form': form,
        'products_with_images': products_with_images,
        'selected_products': selected_products,
    })




# Создание заказа для конкретного клиента
def create_order_for_customer(request):
    """
    Создание заказа для конкретного клиента.
    Если клиент отсутствует в сессии, сначала создаем его.
    """
    customer_id = request.session.get('customer_id')

    if customer_id:
        customer = get_object_or_404(Customer, pk=customer_id)
    else:
        if request.method == 'POST':
            customer_form = CustomerForm(request.POST)
            if customer_form.is_valid():
                customer = customer_form.save()
                request.session['customer_id'] = customer.id
                return redirect('create_order_for_customer')
            else:
                return render(request, 'main/create_customer.html', {'form': customer_form})
        else:
            return render(request, 'main/create_customer.html', {'form': CustomerForm()})

    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.save()
            form.save_m2m()
            return redirect('order_list')  # Перенаправляем в список заказов после создания
    else:
        form = CustomerOrderForm()

    return render(request, 'main/create_order.html', {'form': form})


# Редактирование заказа
def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)

    return render(request, 'main/edit_order.html', {'form': form, 'order': order})



def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Перенаправляем на список товаров
    else:
        form = ProductForm()

    return render(request, 'main/product_form.html', {'form': form})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'main/order_detail.html', {'order': order})
