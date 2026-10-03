from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_POST

from accounts.decorators import staff_required
from accounts.utils import get_user_profile
from catalog.forms import ProductForm, ReviewForm, SiteSettingsForm
from catalog.content import apply_content_lists
from catalog.images import add_single_image, save_product_images, set_primary
from catalog.models import Product, ProductImage, ProductReview, SiteSettings
from orders.models import Order, OrderStatus

_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _wants_json(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    return "application/json" in (request.headers.get("Accept") or "").lower()


def _fa_money(n):
    try:
        return f"{int(n):,}".replace(",", "٬").translate(_FA) + " تومان"
    except (TypeError, ValueError):
        return str(n)


def _fa_num(n):
    try:
        return f"{int(n):,}".replace(",", "٬").translate(_FA)
    except (TypeError, ValueError):
        return str(n)


def _star_glyphs(n):
    try:
        n = int(round(float(n)))
    except (TypeError, ValueError):
        n = 0
    n = max(0, min(5, n))
    return ("★" * n) + ("☆" * (5 - n))


def _serialize_product(p):
    return {
        "id": p.pk,
        "name": p.name,
        "process": p.process,
        "quality": p.quality,
        "stars": p.stars,
        "stars_html": "".join(
            f'<span class="{"is-on" if i <= p.stars else ""}">★</span>' for i in range(1, 6)
        ),
        "wholesale_price": p.wholesale_price,
        "retail_price": p.retail_price,
        "wholesale_text": _fa_money(p.wholesale_price),
        "retail_text": _fa_money(p.retail_price),
        "featured": p.featured,
        "url": reverse("product_detail", args=(p.pk,)),
        "image": p.cover_url() or "",
    }


@ensure_csrf_cookie
def home(request):
    featured = Product.objects.filter(is_active=True, featured=True)[:4]
    deals = Product.objects.filter(is_active=True, on_deal=True)[:4]
    return render(
        request,
        "storefront/home.html",
        {"featured_products": featured, "deal_products": deals, "nav_active": "home"},
    )


def _product_search_qs(q):
    from django.db.models import Case, IntegerField, Q, When

    qs = Product.objects.filter(is_active=True).prefetch_related("images")
    q = (q or "").strip()
    if not q:
        return qs.none()
    qs = qs.filter(
        Q(name__icontains=q)
        | Q(description__icontains=q)
        | Q(details_text__icontains=q)
        | Q(process__icontains=q)
        | Q(quality__icontains=q)
        | Q(weight__icontains=q)
    )
    # Prefer name matches, then featured products
    return qs.annotate(
        rank=Case(
            When(name__icontains=q, then=0),
            When(featured=True, then=1),
            default=2,
            output_field=IntegerField(),
        )
    ).order_by("rank", "name")


def product_search_api(request):
    """Live search suggestions for the header (JSON)."""
    q = request.GET.get("q", "").strip()
    limit = 6
    try:
        limit = min(12, max(1, int(request.GET.get("limit", 6))))
    except (TypeError, ValueError):
        limit = 6
    results = []
    for p in _product_search_qs(q)[:limit]:
        cover = p.cover_url() or ""
        results.append(
            {
                "id": p.pk,
                "name": p.name,
                "process": p.process,
                "quality": p.quality,
                "price": p.retail_price,
                "featured": p.featured,
                "url": reverse("product_detail", args=(p.pk,)),
                "image": cover,
            }
        )
    return JsonResponse({"ok": True, "q": q, "count": len(results), "results": results})


def _filtered_products(request):
    qs = Product.objects.filter(is_active=True).prefetch_related("images")
    q = request.GET.get("q", "").strip()
    process = request.GET.get("process", "all") or "all"
    quality = request.GET.get("quality", "all") or "all"
    sort = request.GET.get("sort", "featured") or "featured"

    if q:
        qs = _product_search_qs(q)
    if process != "all":
        qs = qs.filter(process=process)
    if quality != "all":
        qs = qs.filter(quality=quality)

    if sort == "price-asc":
        qs = qs.order_by("retail_price")
    elif sort == "price-desc":
        qs = qs.order_by("-retail_price")
    elif sort == "name":
        qs = qs.order_by("name")
    else:
        qs = qs.order_by("-featured", "name")
    return qs, q, process, quality, sort


def product_list(request):
    qs, q, process, quality, sort = _filtered_products(request)
    count = qs.count()

    if _wants_json(request):
        return JsonResponse(
            {
                "ok": True,
                "q": q,
                "process": process,
                "quality": quality,
                "sort": sort,
                "count": count,
                "count_text": _fa_num(count),
                "products": [_serialize_product(p) for p in qs],
            }
        )

    processes = Product.objects.filter(is_active=True).values_list("process", flat=True).distinct()
    qualities = Product.objects.filter(is_active=True).values_list("quality", flat=True).distinct()
    deals = Product.objects.filter(is_active=True, on_deal=True)

    return render(
        request,
        "storefront/products.html",
        {
            "products": qs,
            "q": q,
            "process": process,
            "quality": quality,
            "sort": sort,
            "processes": sorted(set(processes)),
            "qualities": sorted(set(qualities)),
            "deal_products": deals,
            "product_count": count,
            "nav_active": "products",
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "reviews"),
        pk=pk,
        is_active=True,
    )
    related = (
        Product.objects.filter(is_active=True, quality=product.quality)
        .exclude(pk=product.pk)
        .prefetch_related("images")[:3]
    )
    reviews = product.reviews.filter(is_public=True)
    stats = product.review_stats()
    review_form = ReviewForm()
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        if profile and profile.full_name:
            review_form = ReviewForm(initial={"author_name": profile.full_name, "stars": 5})
        else:
            review_form = ReviewForm(initial={"author_name": request.user.username, "stars": 5})
    return render(
        request,
        "storefront/product_detail.html",
        {
            "product": product,
            "related_products": related,
            "nav_active": "products",
            "reviews": reviews,
            "review_stats": stats,
            "review_form": review_form,
            "open_review_form": request.GET.get("review") == "1",
        },
    )


@require_http_methods(["POST"])
def product_review_create(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    form = ReviewForm(request.POST)
    if not form.is_valid():
        if _wants_json(request):
            errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
            return JsonResponse(
                {"ok": False, "message": "نظر ثبت نشد — لطفاً همه فیلدها را کامل کنید", "errors": errors},
                status=400,
            )
        messages.error(request, "نظر ثبت نشد — لطفاً همه فیلدها را کامل کنید")
        return redirect(reverse("product_detail", args=[pk]) + "?review=1")
    review = form.save(commit=False)
    review.product = product
    if request.user.is_authenticated:
        review.user = request.user
        verified = Order.objects.filter(
            user=request.user,
            items__product=product,
        ).exclude(status=OrderStatus.CANCELLED).exists()
        review.verified = verified
        profile = get_user_profile(request.user)
        if profile and profile.full_name and not review.author_name:
            review.author_name = profile.full_name
    review.save()
    if _wants_json(request):
        stats = product.review_stats()
        return JsonResponse(
            {
                "ok": True,
                "message": "نظر شما ثبت شد",
                "stats": {
                    "count": stats["count"],
                    "count_text": _fa_num(stats["count"]),
                    "avg_text": stats["avg_text"],
                    "stars": _star_glyphs(stats["avg"]),
                },
                "review": {
                    "author_name": review.author_name,
                    "title": review.title,
                    "body": review.body,
                    "stars": review.stars,
                    "stars_glyphs": _star_glyphs(review.stars),
                    "verified": review.verified,
                    "date": review.created_at.strftime("%Y/%m/%d"),
                    "product_label": f"{product.name} — {product.quality}",
                },
            }
        )
    messages.success(request, "نظر شما ثبت شد")
    return redirect("product_detail", pk=pk)


@staff_required
def staff_products(request):
    products = Product.objects.all().prefetch_related("images").order_by("-created_at", "name")
    return render(
        request,
        "staff/products.html",
        {
            "products": products,
            "active_nav": "products",
            "total_count": products.count(),
            "active_count": products.filter(is_active=True).count(),
            "deal_count": products.filter(on_deal=True).count(),
            "featured_count": products.filter(featured=True).count(),
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def staff_product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        save_product_images(request, product)
        apply_content_lists(request, product)
        messages.success(
            request,
            f"محصول «{product.name}» ثبت شد. می‌توانید تصویر و محتوا را کامل کنید.",
        )
        return redirect("staff_product_edit", pk=product.pk)
    return render(
        request,
        "staff/product_form.html",
        {
            "form": form,
            "active_nav": "products",
            "mode": "create",
            "page_title": "افزودن محصول",
            "existing_images": [],
            "product": None,
        },
    )


@staff_required
@require_http_methods(["GET", "POST"])
def staff_product_edit(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related("images"), pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        save_product_images(request, product)
        apply_content_lists(request, product)
        messages.success(request, f"محصول «{product.name}» به‌روزرسانی شد")
        return redirect("staff_product_edit", pk=product.pk)
    return render(
        request,
        "staff/product_form.html",
        {
            "form": form,
            "product": product,
            "active_nav": "products",
            "mode": "edit",
            "page_title": "ویرایش محصول",
            "existing_images": product.images.all(),
        },
    )


@staff_required
@require_POST
def staff_product_image_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    uploaded = request.FILES.get("image") or request.FILES.get("images")
    if not uploaded:
        return JsonResponse({"ok": False, "error": "فایلی ارسال نشد"}, status=400)
    make_primary = request.POST.get("make_primary") in ("1", "true", "on", "yes")
    img = add_single_image(product, uploaded, make_primary=make_primary)
    return JsonResponse(
        {
            "ok": True,
            "id": img.id,
            "url": img.image.url,
            "is_primary": img.is_primary,
        }
    )


@staff_required
@require_POST
def staff_product_image_primary(request, pk, image_id):
    product = get_object_or_404(Product, pk=pk)
    if not set_primary(product, image_id):
        return JsonResponse({"ok": False, "error": "تصویر پیدا نشد"}, status=404)
    return JsonResponse({"ok": True, "id": image_id})


@staff_required
@require_POST
def staff_product_image_delete(request, pk, image_id):
    product = get_object_or_404(Product, pk=pk)
    img = get_object_or_404(ProductImage, product=product, pk=image_id)
    img.delete()
    from catalog.images import ensure_one_primary

    ensure_one_primary(product)
    primary = product.primary_image
    return JsonResponse(
        {
            "ok": True,
            "primary_id": primary.id if primary else None,
            "cover_url": primary.image.url if primary else None,
        }
    )


@staff_required
@require_POST
def staff_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    try:
        product.delete()
        messages.success(request, f"محصول «{name}» حذف شد")
    except ProtectedError:
        product.is_active = False
        product.save(update_fields=["is_active"])
        messages.warning(
            request,
            f"محصول «{name}» در سفارش‌ها استفاده شده؛ به‌جای حذف، غیرفعال شد.",
        )
    return redirect("staff_products")


@staff_required
def staff_user_handling(request):
    """Inbox for customer reviews — reply / moderate."""
    tab = (request.GET.get("tab") or "pending").strip()
    qs = ProductReview.objects.select_related("product", "user").order_by("-created_at")
    pending_qs = qs.filter(Q(reply_body="") | Q(reply_body__isnull=True))
    if tab == "replied":
        reviews = qs.exclude(Q(reply_body="") | Q(reply_body__isnull=True))
    elif tab == "all":
        reviews = qs
    else:
        tab = "pending"
        reviews = pending_qs
    return render(
        request,
        "staff/user_handling.html",
        {
            "reviews": reviews,
            "tab": tab,
            "pending_count": pending_qs.count(),
            "all_count": qs.count(),
            "replied_count": qs.exclude(Q(reply_body="") | Q(reply_body__isnull=True)).count(),
            "active_nav": "user_handling",
        },
    )


@staff_required
@require_POST
def staff_review_reply(request, review_id):
    review = get_object_or_404(ProductReview.objects.select_related("product"), pk=review_id)
    body = (request.POST.get("reply_body") or "").strip()
    name = (request.POST.get("reply_name") or "").strip() or "برنج رودی"
    if not body:
        messages.error(request, "متن پاسخ خالی است")
        return redirect("staff_user_handling")
    review.reply_body = body
    review.reply_name = name
    review.replied_at = timezone.now()
    if request.POST.get("hide") == "1":
        review.is_public = False
    review.save(update_fields=["reply_body", "reply_name", "replied_at", "is_public"])
    messages.success(request, f"پاسخ برای نظر «{review.title}» ثبت شد")
    next_tab = request.POST.get("next_tab") or "pending"
    return redirect(f"{reverse('staff_user_handling')}?tab={next_tab}")


@staff_required
@require_POST
def staff_review_toggle(request, review_id):
    review = get_object_or_404(ProductReview, pk=review_id)
    review.is_public = not review.is_public
    review.save(update_fields=["is_public"])
    messages.success(request, "وضعیت نمایش نظر به‌روز شد")
    return redirect(request.POST.get("next") or "staff_user_handling")


@staff_required
@require_http_methods(["GET", "POST"])
def staff_site_settings(request):
    settings_obj = SiteSettings.load()
    form = SiteSettingsForm(request.POST or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات تماس و درباره ما ذخیره شد")
        return redirect("staff_site_settings")
    return render(
        request,
        "staff/site_settings.html",
        {
            "form": form,
            "active_nav": "site_settings",
            "page_title": "اطلاعات فروشگاه",
        },
    )
