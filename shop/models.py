from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('manager', 'Manager'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    inn = models.CharField(max_length=12, blank=True, null=True, verbose_name="ИНН")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="Пол")

    # Переопределение полей groups и user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='shop_users',  # Изменяем related_name
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='shop_users_permissions',  # Изменяем related_name
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username

class Shop(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Название магазина"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shops", verbose_name=_("Владелец"))
    inn = models.CharField(max_length=12, verbose_name=_("ИНН"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    email = models.EmailField(verbose_name=_("Email магазина"))

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('bottoms', _('Низ')),
        ('underwear', _('Нижнее белье')),
        ('tops', _('Верх')),
        ('headwear', _('Голова')),
    )
    SIZE_CHOICES = (
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
    )

    name = models.CharField(max_length=255, verbose_name=_("Название товара"))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name=_("Категория"))
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, verbose_name=_("Размер"))
    color = models.CharField(max_length=50, verbose_name=_("Цвет"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    quantity = models.PositiveIntegerField(verbose_name=_("Количество"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products", verbose_name=_("Магазин"))
    image1 = models.ImageField(upload_to='products/', verbose_name=_("Изображение 1"))
    image2 = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("Изображение 2"))

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return round(total_rating / reviews.count(), 1)  # Округляем до одного знака после запятой
        return 0  # Если отзывов нет, возвращаем 0

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('В обработке')),
        ('shipped', _('Отправлен')),
        ('delivered', _('Доставлен')),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Пользователь"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(verbose_name=_("Количество"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart", verbose_name=_("Пользователь"))

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Корзина"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats", verbose_name=_("Участники"))
    last_message = models.TextField(blank=True, null=True, verbose_name=_("Последнее сообщение"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    def __str__(self):
        return f"Чат #{self.id}"

    def can_user_access(self, user):
        """
        Проверяет, может ли пользователь получить доступ к этому чату.
        """
        if user.role == 'seller':
            # Продавец может общаться только с покупателями, которые оставили отзыв
            return self.participants.filter(role='buyer', reviews__product__shop__owner=user).exists()
        elif user.role == 'buyer':
            # Покупатель может общаться с любым продавцом
            return self.participants.filter(role='seller').exists()
        return False

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages", verbose_name=_("Чат"))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages", verbose_name=_("Отправитель"))
    text = models.TextField(verbose_name=_("Текст сообщения"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Время отправки"))

    def __str__(self):
        return f"Сообщение от {self.sender.username}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("Пользователь"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("Товар"))
    rating = models.PositiveIntegerField(verbose_name=_("Оценка"))
    comment = models.TextField(blank=True, null=True, verbose_name=_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"