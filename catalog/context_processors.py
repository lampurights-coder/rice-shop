from django.db.models import Q

from catalog.models import ProductReview, SiteSettings


def staff_notifications(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or not user.is_staff:
        return {"staff_unreplied_count": 0}
    count = (
        ProductReview.objects.filter(is_public=True)
        .filter(Q(reply_body="") | Q(reply_body__isnull=True))
        .count()
    )
    return {"staff_unreplied_count": count}


def site_settings(request):
    try:
        return {"site": SiteSettings.load()}
    except Exception:
        return {"site": None}
