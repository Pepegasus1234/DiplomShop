from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import User, Shop, Product, Order, Cart, CartItem, Review, Chat, Message
from .forms import BuyerRegistrationForm, SellerRegistrationForm, LoginForm, AddManagerForm, ShopInfoForm, ProductForm, ReviewForm, ProfileEditForm, CustomPasswordChangeForm
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from yookassa import Configuration
from yookassa import Payment as YooKassaPayment
from django.conf import settings
from django.urls import reverse

Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

# Главная страница
def home(request):
    products = Product.objects.all()[:8]  # Последние 8 товаров
    return render(request, 'home.html', {'products': products})
# Авторизация
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            inn = form.cleaned_data['inn']
            user = authenticate(request, username=username, password=password)
            if user:
                if user.role == 'seller' and not inn:
                    form.add_error('inn', "Для входа как продавец укажите ИНН.")
                elif user.role == 'seller' and user.inn != inn:
                    form.add_error('inn', "Неверный ИНН.")
                else:
                    login(request, user)
                    return redirect('shop:profile')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Выход из аккаунта
@login_required
def logout_view(request):
    logout(request)
    return redirect('shop:home')

# Регистрация покупателя
def register_buyer(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:login')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'register_buyer.html', {'form': form})

# Регистрация продавца
def register_seller(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя
            user = form.save(commit=False)
            user.role = 'seller'  # Устанавливаем роль "продавец"
            user.save()

            shop = Shop.objects.create(
                name=f"{user.username}'s Shop",  # Имя магазина по умолчанию
                owner=user,
                inn=form.cleaned_data['inn'],  # ИНН из формы
                email=form.cleaned_data['email']  # Email из формы
            )
            shop.save()

            # Авторизуем пользователя
            login(request, user)
            return redirect('shop:home')
    else:
        form = SellerRegistrationForm()

    return render(request, 'register_seller.html', {'form': form})

# Профиль пользователя
@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user) if user.role == 'buyer' else None

    tab = request.GET.get('tab', 'profile')
    form = None

    if tab == 'password':
        if request.method == 'POST':
            form = CustomPasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Обновляем сессию пользователя после изменения пароля
                messages.success(request, 'Ваш пароль успешно изменен!')
                return redirect('shop:profile')
        else:
            form = CustomPasswordChangeForm(request.user)
    elif tab == 'profile':
        if request.method == 'POST':
            form = ProfileEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ваш профиль успешно обновлен!')
                return redirect('shop:profile')
        else:
            form = ProfileEditForm(instance=user)

    return render(request, 'profile.html', {'user': user, 'orders': orders, 'form': form, 'tab': tab})

# Заказы
@login_required
def orders(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    return render(request, 'orders.html', {'orders': orders})

# Чаты
@login_required
def chats(request):
    user = request.user
    chats = Chat.objects.filter(participants=user)

    # Добавляем имя второго участника чата
    for chat in chats:
        other_participant = chat.participants.exclude(id=user.id).first()
        chat.other_participant_username = other_participant.username if other_participant else "Неизвестный пользователь"

    return render(request, 'profile.html', {'chats': chats})
@login_required
def create_chat(request):
    user = request.user

    # Определяем, с кем может общаться пользователь
    if user.role == 'buyer':
        # Покупатель может общаться с любым продавцом
        available_users = User.objects.filter(role='seller')
    elif user.role == 'seller':
        # Продавец может общаться только с покупателями, которые оставили отзыв
        available_users = User.objects.filter(
            role='buyer',
            reviews__product__shop__owner=user
        ).distinct()
    else:
        available_users = []

    if request.method == 'POST':
        participant_id = request.POST.get('participant_id')
        if participant_id:
            participant = User.objects.get(id=participant_id)

            # Проверяем, существует ли уже чат между этими пользователями
            chat = Chat.objects.filter(participants=user).filter(participants=participant).first()
            if not chat:
                # Создаем новый чат
                chat = Chat.objects.create(last_message="")
                chat.participants.add(user, participant)
                chat.save()

            return redirect('shop:chat_detail', chat_id=chat.id)

    return render(request, 'create_chat.html', {'available_users': available_users})

@login_required
def chat_detail(request, chat_id):
    # Получаем чат по ID и проверяем, имеет ли пользователь доступ к этому чату
    chat = get_object_or_404(Chat, id=chat_id)
    if not chat.participants.filter(id=request.user.id).exists():
        # Если пользователь не является участником чата, перенаправляем его
        return redirect('shop:profile')

    # Получаем все сообщения из этого чата
    messages = chat.messages.all().order_by('timestamp')

    # Обработка отправки нового сообщения
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user, text=text)
            chat.last_message = text
            chat.save()
            return redirect('shop:chat_detail', chat_id=chat.id)

    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages})

@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Проверяем, имеет ли пользователь доступ к этому чату
    if not chat.can_user_access(request.user):
        return redirect('shop:profile')

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user, text=text)
            chat.last_message = text
            chat.save()
            return redirect('shop:chat_detail', chat_id=chat.id)

    return redirect('shop:profile')

# Каталог товаров
def catalog(request):
    # Получаем параметры из GET-запроса
    category = request.GET.get('category')
    size = request.GET.get('size')
    sort_by = request.GET.get('sort_by')  # Новый параметр для сортировки

    # Базовый запрос для всех товаров
    products = Product.objects.all()

    # Фильтрация по категории
    if category:
        products = products.filter(category=category)

    # Фильтрация по размеру
    if size:
        products = products.filter(size=size)

    # Сортировка по цене
    if sort_by == 'price_asc':
        products = products.order_by('price')  # По возрастанию цены
    elif sort_by == 'price_desc':
        products = products.order_by('-price')  # По убыванию цены

    # Передача данных в шаблон
    return render(request, 'catalog.html', {
        'products': products,
        'category': category,
        'size': size,
        'sort_by': sort_by,  # Передаем выбранный параметр сортировки
    })

# Карточка товара
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    tab = request.GET.get('tab', 'about_product')  # По умолчанию открывается вкладка "О товаре"

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('shop:product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'tab': tab,
    })

@login_required
def cart(request):
    user = request.user
    cart = Cart.objects.get_or_create(user=user)[0]
    cart_items = cart.items.all()
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Добавление товара в корзину
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({'message': 'Product added to cart'})

# Корзина пользователя
@login_required
def view_cart(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    cart_items = cart.items.all()
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Удаление товара из корзины
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:view_cart')

# Администрирование магазина
@login_required
def admin_shop(request, tab='my_shop'):
    if request.user.role != 'seller':
        return redirect('shop:home')

    shop = Shop.objects.get(owner=request.user)
    products = Product.objects.filter(shop=shop)

    # Форма для редактирования информации о магазине
    shop_info_form = ShopInfoForm(instance=shop)
    if request.method == 'POST' and 'edit_shop_info' in request.POST:
        shop_info_form = ShopInfoForm(request.POST, instance=shop)
        if shop_info_form.is_valid():
            shop_info_form.save()
            messages.success(request, 'Информация о магазине успешно обновлена!')

    # Форма для добавления менеджера
    add_manager_form = AddManagerForm()
    if request.method == 'POST' and 'add_manager' in request.POST:
        add_manager_form = AddManagerForm(request.POST)
        if add_manager_form.is_valid():
            user = add_manager_form.cleaned_data['username']
            user.role = 'manager'
            user.save()
            messages.success(request, f'Пользователь {user.username} успешно добавлен как менеджер.')

    # Получение заказов, связанных с текущим магазином
    orders = Order.objects.filter(product__shop=shop)

    # Получение товаров на складе
    stock_products = Product.objects.filter(shop=shop)

    # Получение данных для аналитики
    top_products = Product.objects.filter(shop=shop).annotate(total_quantity=models.Sum('orders__quantity')).order_by('-total_quantity')[:5]
    income_data = Order.objects.filter(product__shop=shop).values('created_at__date').annotate(total_income=models.Sum('product__price'))

    # Форма для добавления товара
    product_form = ProductForm()
    if request.method == 'POST' and 'add_product' in request.POST:
        print('i got form 1')
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            print('i got form 2')
            product = product_form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('shop:admin_shop', tab='stock')

    return render(request, 'admin_shop.html', {
        'shop': shop,
        'products': products,
        'shop_info_form': shop_info_form,
        'add_manager_form': add_manager_form,
        'orders': orders,
        'stock_products': stock_products,
        'top_products': top_products,
        'income_data': income_data,
        'product_form': product_form,
        'tab': tab,
    })

@login_required
def update_order_status(request, order_id):
    if request.user.role != 'seller':
        return redirect('shop:home')

    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        order.status = status
        order.save()
        messages.success(request, 'Статус заказа успешно обновлен.')
        return redirect('shop:admin_shop', tab='completed_orders')

    return redirect('shop:admin_shop', tab='completed_orders')

@login_required
def delete_product(request, product_id):
    if request.user.role != 'seller':
        return redirect('shop:home')

    product = get_object_or_404(Product, id=product_id, shop__owner=request.user)
    product.delete()
    messages.success(request, 'Товар успешно удален!')
    return redirect('shop:admin_shop', tab='stock')

@login_required
def create_payment(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)  # Получаем все товары в корзине

    # Вычисляем общую стоимость всех товаров в корзине
    total_price = sum(item.total_price() for item in cart_items)

    if not cart_items:
        return redirect('shop:view_cart')

    # Создаем заказы для каждого товара в корзине
    for item in cart_items:
        Order.objects.create(
            user=user,
            product=item.product,
            quantity=item.quantity,
            status='pending'
        )

    # Очищаем корзину: удаляем все связанные объекты CartItem
    CartItem.objects.filter(cart=cart).delete()

    # Создаем платеж в YooKassa
    payment = YooKassaPayment.create({
        "amount": {
            "value": str(total_price),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": request.build_absolute_uri(reverse('shop:payment_confirmation'))
        },
        "capture": True,
        "description": f"Оплата заказов на сумму {total_price} RUB"
    })

    # Перенаправляем пользователя на страницу подтверждения платежа
    confirmation_url = payment.confirmation.confirmation_url
    return redirect(confirmation_url) # pragma: no cover

def payment_confirmation(request):
    payment_id = request.GET.get('payment_id')
    if payment_id:
        try:
            # Получаем информацию о платеже
            payment = YooKassaPayment.find_one(payment_id)

            if payment.status == 'succeeded' and payment.paid:
                # Получаем данные о заказе
                order_id = payment.metadata.get('order_id')
                order = Order.objects.get(id=order_id)
                return render(request, 'payment_confirmation.html', {
                    'success': True,
                    'payment_amount': payment.amount.value,
                    'payment_date': payment.created_at,
                    'order_id': order_id
                })
            elif payment.status == 'pending':
                return render(request, 'payment_confirmation.html', {
                    'success': False,
                    'message': 'Платеж ожидает подтверждения.'
                })
            else:
                return render(request, 'payment_confirmation.html', {
                    'success': False,
                    'message': 'Ошибка при обработке платежа.'
                })
        except Exception as e:
            return render(request, 'payment_confirmation.html', {
                'success': False,
                'message': f'Произошла ошибка: {str(e)}'
            })
    return render(request, 'payment_confirmation.html', {'success': False})