from datetime import datetime
from .models import Product
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .forms import OrderForm
from .models import Customer, Order
from .forms import CustomerOrderForm
from .models import UserProfile  # Если используете профиль для хранения телефона
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib import messages



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


# views.py
def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Сохраняем нового пользователя
            user = user_form.save()

            # Создаем профиль пользователя с номером телефона
            profile = profile_form.save(commit=False)
            profile.user = user  # Привязываем профиль к пользователю
            profile.save()

            messages.success(request, 'Ваш аккаунт успешно создан!')
            return redirect('login')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'main/register.html', {'user_form': user_form, 'profile_form': profile_form})



# Создание заказа
# Создание заказа
def create_order(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы должны быть авторизованы для создания заказа.")

    user = request.user

    # Проверка на существование профиля и создание, если необходимо
    if not hasattr(user, 'profile'):
        # Проверяем, существует ли уже профиль с таким телефоном
        phone = request.user.profile.phone if user.profile else None

        # Проверка на уникальность телефона
        if phone and UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Профиль с таким номером телефона уже существует.")
            return redirect('update_profile')

        # Если профиль не существует, создаем новый
        user.profile = UserProfile.objects.create(user=user)
        print(f"Профиль для пользователя {user.username} был создан")

    # Получаем номер телефона из профиля пользователя
    phone = user.profile.phone if user.profile else None

    if not phone:
        messages.error(request, "Пожалуйста, добавьте номер телефона в ваш профиль.")
        return redirect('update_profile')

    # Находим или создаем заказчика
    customer, created = Customer.objects.get_or_create(
        phone=phone,
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
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})


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


def update_profile(request):
    if request.method == 'POST':
        # Проверка на существование профиля и создание, если необходимо
        if not hasattr(request.user, 'profile'):
            request.user.profile = UserProfile.objects.create(user=request.user)

        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Перенаправление на страницу профиля или другую
    else:
        # Проверка на существование профиля и создание, если необходимо
        if not hasattr(request.user, 'profile'):
            request.user.profile = UserProfile.objects.create(user=request.user)

        form = UserProfileForm(instance=request.user.profile)

    return render(request, 'update_profile.html', {'form': form})
