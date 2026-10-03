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
    delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="تاریخ تحویل درخواستی مشتری",
    )
    postal_code = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    stock_deducted = models.BooleanField(
        default=False,
        help_text="اگر موجودی انبار برای این سفارش کم شده باشد True است",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_cancelable(self):
        return self.status == OrderStatus.PROCESSING

    def apply_stock(self):
        """Decrease warehouse kg for each line. Returns (ok, error_message)."""
        if self.stock_deducted:
            return True, ""
        from django.db import transaction

        with transaction.atomic():
            for item in self.items.select_related("product"):
                product = item.product
                if not product:
                    continue
                ok, need = product.decrease_stock(item.quantity)
                if not ok:
                    raise ValueError(
                        f"موجودی «{item.product_name}» کافی نیست (نیاز: {need} کیلو)"
                    )
            self.stock_deducted = True
            self.save(update_fields=["stock_deducted"])
        return True, ""

    def restore_stock(self):
        """Put kg back when an order is cancelled after stock was taken."""
        if not self.stock_deducted:
            return
        for item in self.items.select_related("product"):
            if item.product_id:
                item.product.increase_stock(item.quantity)
        self.stock_deducted = False
        self.save(update_fields=["stock_deducted"])

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
