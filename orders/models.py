from django.conf import settings
from django.db import models
from django.utils import timezone

from catalog.models import Product


class OrderStatus(models.TextChoices):
    PROCESSING = "processing", "در حال آماده‌سازی"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل شده"
    CANCELLED = "cancelled", "لغو شده"


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "product")]
        ordering = ["-created_at"]

    @property
    def line_total(self):
        return self.product.retail_price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    code = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING,
    )
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_cancelable(self):
        return self.status == OrderStatus.PROCESSING

    @property
    def items_summary(self):
        parts = [f"{item.product_name} × {item.quantity}" for item in self.items.all()]
        return "، ".join(parts)

    @classmethod
    def generate_code(cls):
        stamp = timezone.now().strftime("%y%m%d%H%M%S")
        return f"ORD-{stamp}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    weight = models.CharField(max_length=40, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.unit_price * self.quantity
