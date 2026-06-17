from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class CartStockTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Solar Solutions')
        self.product = Product.objects.create(
            name='Solar Panel 400W',
            description='High-efficiency panel',
            price=120000,
            category=self.category,
            product_type='cart',
            stock=2,
            reorder_level=1,
        )

    def test_add_to_cart_rejects_quantity_above_available_stock(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_to_cart', args=[self.product.id]),
            {'quantity': 3},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('stock', data['error'])
