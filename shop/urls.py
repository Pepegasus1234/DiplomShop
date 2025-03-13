from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'shop'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Авторизация и регистрация
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/seller/', views.register_seller, name='register_seller'),

    # Профиль пользователя
    path('profile/', views.profile, name='profile'),
    path('profile/cart/', views.cart, name='cart'),
    path('profile/orders/', views.orders, name='orders'),
    path('profile/chats/', views.chats, name='chats'),

    # Администрирование магазина
    path('administration/<str:tab>/', views.admin_shop, name='admin_shop'),
    # Дефолтная таба
    path('administration/', views.admin_shop, {'tab': 'my_shop'}, name='admin_shop_default'),\
    # Удаление со склада
    path('administration/delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    # Обновление статуса заказа
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),

    # Каталог товаров
    path('catalog/', views.catalog, name='catalog'),

    # Карточка товара
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Корзина
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Чаты
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('create_chat/', views.create_chat, name='create_chat'),
    path('send_message/<int:chat_id>/', views.send_message, name='send_message'),

    path('create_payment/', views.create_payment, name='create_payment'),
    path('payment_confirmation/', views.payment_confirmation, name='payment_confirmation'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)