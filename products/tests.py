from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, ProductReview


class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Solar Solutions')
        self.product = Product.objects.create(
            name='Solar Panel 400W',
            description='High-efficiency solar panel for commercial use.',
            price=120000,
            category=self.category,
            product_type='cart',
            stock=12,
            reorder_level=5,
        )
        self.other_product = Product.objects.create(
            name='Battery Pack 10kWh',
            description='Reliable battery storage for solar systems.',
            price=95000,
            category=self.category,
            product_type='cart',
            stock=8,
            reorder_level=4,
        )
        ProductReview.objects.create(
            product=self.product,
            name='Jane',
            rating=5,
            comment='Works perfectly and arrived on time.',
        )

    def test_product_detail_exposes_recently_viewed_and_review_summary(self):
        session = self.client.session
        session['recently_viewed'] = [self.other_product.id, self.product.id]
        session.save()

        response = self.client.get(reverse('product_detail', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('recently_viewed_products', response.context)
        self.assertIn('review_summary', response.context)
        self.assertEqual(response.context['review_summary']['average_rating'], 5.0)
        self.assertEqual(len(response.context['recently_viewed_products']), 1)
        self.assertEqual(response.context['recently_viewed_products'][0].id, self.other_product.id)

    def test_product_detail_updates_recently_viewed_session(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['recently_viewed'][:1], [self.product.id])
