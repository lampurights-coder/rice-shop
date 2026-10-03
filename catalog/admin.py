from django.contrib import admin

from catalog.models import Product, ProductImage, ProductReview, SiteSettings


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    fields = ("author_name", "title", "stars", "verified", "is_public", "reply_body")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "process",
        "quality",
        "weight",
        "stock_kg",
        "low_stock_kg",
        "retail_price",
        "featured",
        "on_deal",
        "is_active",
    )
    list_filter = ("process", "quality", "featured", "on_deal", "is_active")
    search_fields = ("name", "description")
    list_editable = ("stock_kg", "low_stock_kg", "is_active", "featured", "on_deal")
    inlines = [ProductImageInline, ProductReviewInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary", "sort_order", "created_at")
    list_filter = ("is_primary",)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author_name", "title", "stars", "verified", "is_public", "created_at")
    list_filter = ("stars", "verified", "is_public")
    search_fields = ("title", "body", "author_name", "product__name")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "email", "working_hours", "updated_at")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
