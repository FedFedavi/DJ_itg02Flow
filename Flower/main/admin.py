from django.contrib import admin
from django.contrib.auth.models import User
from .models import Product, Order


# Настройка отображения для модели Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)

# Настройка отображения для модели Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')

# Регистрация моделей с настройками
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)