from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order, OrderItem
from payments.utils import reduce_stock_for_order
from products.models import Category, Product


class PaymentStockTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Solar Solutions')
        self.product = Product.objects.create(
            name='Battery Pack 10kWh',
            description='Energy storage pack',
            price=95000,
            category=self.category,
            product_type='cart',
            stock=10,
            reorder_level=2,
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=190000,
            status='pending',
            is_paid=False,
            delivery_address='Nairobi',
            phone='0712345678',
            accepted_terms=True,
            accepted_privacy=True,
            accepted_warranty=True,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=self.product.price,
        )

    def test_reduce_stock_for_order_deducts_quantities(self):
        reduce_stock_for_order(self.order)

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 7)
