from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.user_list, name='user'),
    path('products/', views.product_list, name='product_list'),
    path('orders/', views.order_list, name='order_list'),
    path('register/', views.register, name='register'),
    path('create_order/', views.create_order, name='create_order'),
]