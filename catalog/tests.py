from django.core.management import call_command
from django.test import TestCase

from catalog.models import Product


class SeedProductsTest(TestCase):
    def test_seed_products_command(self):
        call_command("seed_products")
        self.assertGreaterEqual(Product.objects.count(), 12)
