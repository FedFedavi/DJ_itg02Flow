from datetime import datetime
from .models import Product, Customer, Order, UserProfile
from .forms import OrderForm, CustomerForm, UserProfileForm, RegistrationForm
from django.http import HttpResponseForbidden
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages


# Главная страница
def index(request):
    context = {
        'current_year': datetime.now().year,
        'products': Product.objects.all(),
    }
    return render(request, 'main/index.html', context)


# Регистрация
def register(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()  # Сохраняем пользователя
            profile = profile_form.save(commit=False)
            profile.user = user  # Связываем профиль с пользователем
            profile.save()  # Сохраняем профиль
            login(request, user)  # Авторизуем пользователя после регистрации
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('index')  # Перенаправляем на главную страницу
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        user_form = RegistrationForm()
        profile_form = UserProfileForm()

    return render(request, 'main/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# Создание заказа
def create_order(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Вы должны быть авторизованы для создания заказа.")

    user = request.user
    # Получаем или создаём профиль пользователя
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if not profile.phone:
        messages.error(request, "Пожалуйста, добавьте номер телефона в ваш профиль.")
        return redirect('update_profile')

    # Находим или создаем заказчика
    customer, _ = Customer.objects.get_or_create(
        phone=profile.phone,
        defaults={'name': user.username, 'email': user.email}
    )

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.customer = customer
            order.save()
            form.save_m2m()
            messages.success(request, "Заказ успешно создан!")
            return redirect('order_list')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = OrderForm()

    return render(request, 'main/create_order.html', {'form': form})


# Обновление профиля
def update_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect('index')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'main/update_profile.html', {'form': form})
