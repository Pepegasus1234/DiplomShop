from django.test import TestCase, Client
from django.urls import reverse
from .models import Product

class CatalogTests(TestCase):
    def setUp(self):
        # Создаем клиента для тестирования
        self.client = Client()

        # Создаем тестовые товары
        self.product1 = Product.objects.create(
            name="Product 1",
            category="tops",
            size="M",
            color="Red",
            price=100,
            quantity=10
        )
        self.product2 = Product.objects.create(
            name="Product 2",
            category="bottoms",
            size="L",
            color="Blue",
            price=200,
            quantity=5
        )
        self.product3 = Product.objects.create(
            name="Product 3",
            category="tops",
            size="S",
            color="Green",
            price=150,
            quantity=8
        )

    def test_catalog_view_all_products(self):
        """
        Тестирование просмотра всех товаров в каталоге.
        """
        url = reverse('shop:catalog')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
        self.assertContains(response, self.product3.name)

    def test_filter_by_category(self):
        """
        Тестирование фильтрации товаров по категории.
        """
        url = reverse('shop:catalog') + '?category=tops'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна
        self.assertContains(response, self.product1.name)  # Продукт из категории "tops"
        self.assertContains(response, self.product3.name)  # Продукт из категории "tops"
        self.assertNotContains(response, self.product2.name)  # Продукт не из категории "tops"

    def test_filter_by_size(self):
        """
        Тестирование фильтрации товаров по размеру.
        """
        url = reverse('shop:catalog') + '?size=M'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна
        self.assertContains(response, self.product1.name)  # Продукт с размером "M"
        self.assertNotContains(response, self.product2.name)  # Продукт с другим размером
        self.assertNotContains(response, self.product3.name)  # Продукт с другим размером

    def test_filter_by_price(self):
        """
        Тестирование фильтрации товаров по цене.
        """
        url = reverse('shop:catalog') + '?min_price=120&max_price=200'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна
        self.assertContains(response, self.product2.name)  # Продукт в диапазоне цен
        self.assertContains(response, self.product3.name)  # Продукт в диапазоне цен
        self.assertNotContains(response, self.product1.name)  # Продукт вне диапазона цен

    def test_sort_by_price_asc(self):
        """
        Тестирование сортировки товаров по возрастанию цены.
        """
        url = reverse('shop:catalog') + '?sort_by=price_asc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна

        # Проверяем порядок товаров
        products = response.context['products']
        self.assertEqual(list(products), [self.product1, self.product3, self.product2])

    def test_sort_by_price_desc(self):
        """
        Тестирование сортировки товаров по убыванию цены.
        """
        url = reverse('shop:catalog') + '?sort_by=price_desc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна

        # Проверяем порядок товаров
        products = response.context['products']
        self.assertEqual(list(products), [self.product2, self.product3, self.product1])

    def test_combined_filters(self):
        """
        Тестирование комбинированных фильтров (категория + размер + цена).
        """
        url = reverse('shop:catalog') + '?category=tops&size=S&min_price=140&max_price=160'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Страница должна быть доступна

        # Проверяем, что отображается только один продукт
        self.assertContains(response, self.product3.name)  # Продукт соответствует всем фильтрам
        self.assertNotContains(response, self.product1.name)  # Не соответствует фильтрам
        self.assertNotContains(response, self.product2.name)  # Не соответствует фильтрам