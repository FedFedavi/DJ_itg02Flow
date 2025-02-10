from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.user_list, name='user'),
    path('products/', views.product_list, name='product_list'),
    path('orders/', views.order_list, name='order_list'),
    path('register/', views.register, name='register'),
    path('create_order/', views.create_order, name='create_order'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create_order_for_customer/', views.create_order_for_customer, name='create_order_for_customer'),
    path('create_order_for_customer/<int:order_id>/', views.create_order_for_customer, name='edit_order_for_customer'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),

]