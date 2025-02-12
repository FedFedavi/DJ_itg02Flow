from .models import Customer, Product, Order
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Импортируем кастомную модель


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'telegram_id')
    search_fields = ('name', 'email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'customer__name')



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('id',)

admin.site.site_header = "Администрирование Django"
admin.site.site_title = "Django Admin"
admin.site.index_title = "Администрирование сайта"
