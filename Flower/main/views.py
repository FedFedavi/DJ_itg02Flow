from django.shortcuts import render
from datetime import datetime
from .models import User, Product, Order


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
    return render(request, 'user_list.html', {'users': users})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'order_list.html', {'orders': orders})
