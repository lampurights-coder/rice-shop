from django.db.models import Q

from catalog.models import Product, ProductReview, SiteSettings


def staff_notifications(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or not user.is_staff:
        return {"staff_unreplied_count": 0, "staff_low_stock_count": 0}
    count = (
        ProductReview.objects.filter(is_public=True)
        .filter(Q(reply_body="") | Q(reply_body__isnull=True))
        .count()
    )
    low_stock_count = sum(
        1 for p in Product.objects.filter(is_active=True).only("stock_kg", "low_stock_kg", "weight")
        if p.is_low_stock
    )
    return {
        "staff_unreplied_count": count,
        "staff_low_stock_count": low_stock_count,
    }


def site_settings(request):
    try:
        return {"site": SiteSettings.load()}
    except Exception:
        return {"site": None}
