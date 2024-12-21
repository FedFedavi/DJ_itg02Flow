from django.contrib import admin
from .models import User, Product, Order


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')  # Поля для отображения в списке
    search_fields = ('name', 'email')  # Поля для поиска
    list_filter = ('email',)  # Фильтры

# Настройка отображения для модели Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)

# Настройка отображения для модели Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    search_fields = ('user__name', 'status')
    list_filter = ('status', 'created_at')

# Регистрация моделей с настройками
admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)