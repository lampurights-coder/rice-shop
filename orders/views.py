from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from accounts.decorators import customer_required, staff_required
from accounts.models import Profile
from accounts.utils import get_user_profile
from catalog.models import Product
from orders.forms import CheckoutForm
from orders.models import CartItem, Order, OrderItem, OrderStatus


def _wants_json(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    return "application/json" in (request.headers.get("Accept") or "").lower()


def _cart_items(user):
    return CartItem.objects.filter(user=user).select_related("product")


def _cart_totals(user):
    items = list(_cart_items(user))
    count = sum(i.quantity for i in items)
    total = sum(i.line_total for i in items)
    return items, count, total


@login_required
def user_dashboard(request):
    if request.user.is_staff:
        return redirect("staff_dashboard")
    items, cart_count, cart_total = _cart_totals(request.user)
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    active = orders.filter(status__in=[OrderStatus.PROCESSING, OrderStatus.SHIPPED]).count()
    delivered = orders.filter(status=OrderStatus.DELIVERED).count()
    profile = get_user_profile(request.user)
    return render(
        request,
        "user/dashboard.html",
        {
            "active_nav": "dashboard",
            "cart_count": cart_count,
            "cart_total": cart_total,
            "active_orders": active,
            "delivered_orders": delivered,
            "recent_orders": orders[:5],
            "profile": profile,
        },
    )


@customer_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    profile = get_user_profile(request.user)
    return render(request, "user/orders.html", {"orders": orders, "active_nav": "orders", "profile": profile})


@customer_required
@require_POST
def order_cancel(request, code):
    order = get_object_or_404(Order, user=request.user, code=code)
    if not order.is_cancelable:
        messages.error(request, "این سفارش قابل لغو نیست")
        return redirect("user_orders")
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if not order.is_cancelable:
            messages.error(request, "این سفارش قابل لغو نیست")
            return redirect("user_orders")
        order.restore_stock()
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status"])
    messages.success(request, "سفارش لغو شد و موجودی به انبار برگشت")
    return redirect("user_orders")


@customer_required
def cart_view(request):
    items, count, total = _cart_totals(request.user)
    return render(
        request,
        "user/cart.html",
        {"cart_items": items, "cart_line_count": count, "cart_total": total, "active_nav": "cart", "profile": get_user_profile(request.user)},
    )


@customer_required
@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        qty = 1
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    new_qty = (item.quantity + qty) if not created else qty
    if not product.can_fulfill(new_qty):
        avail = product.available_packages()
        msg = (
            f"موجودی «{product.name}» کافی نیست"
            + (f" (حداکثر {avail} بسته)" if avail else " (ناموجود)")
        )
        if _wants_json(request):
            return JsonResponse({"ok": False, "message": msg}, status=400)
        messages.error(request, msg)
        return redirect("user_cart")
    item.quantity = new_qty
    item.save()
    _, cart_count, _ = _cart_totals(request.user)
    if _wants_json(request):
        return JsonResponse(
            {
                "ok": True,
                "message": "به سبد اضافه شد",
                "cart_count": cart_count,
                "product_name": product.name,
            }
        )
    messages.success(request, "به سبد اضافه شد")
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("user_cart")


@customer_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    action = request.POST.get("action")
    if action == "remove":
        item.delete()
        messages.success(request, "از سبد حذف شد")
    else:
        try:
            delta = int(request.POST.get("delta", 0))
        except (TypeError, ValueError):
            delta = 0
        new_qty = max(1, item.quantity + delta)
        if not item.product.can_fulfill(new_qty):
            messages.error(
                request,
                f"موجودی کافی نیست (حداکثر {item.product.available_packages()} بسته)",
            )
        else:
            item.quantity = new_qty
            item.save()
    return redirect("user_cart")


@customer_required
@require_http_methods(["GET", "POST"])
def checkout_view(request):
    items = list(_cart_items(request.user))
    if not items:
        messages.error(request, "سبد خرید خالی است")
        return redirect("user_cart")
    for item in items:
        if not item.product.can_fulfill(item.quantity):
            messages.error(
                request,
                f"موجودی «{item.product.name}» کافی نیست — سبد را اصلاح کنید",
            )
            return redirect("user_cart")

    profile = get_user_profile(request.user)
    total = sum(i.line_total for i in items)
    initial = {
        "delivery_date": timezone.localdate() + timedelta(days=2),
        "postal_code": getattr(profile, "postal_code", "") or "",
        "address": getattr(profile, "address", "") or "",
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    code=Order.generate_code(),
                    total=total,
                    delivery_date=data["delivery_date"],
                    postal_code=data["postal_code"],
                    address=data["address"],
                )
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        weight=item.product.weight,
                        quantity=item.quantity,
                        unit_price=item.product.retail_price,
                    )
                order.apply_stock()
                CartItem.objects.filter(user=request.user).delete()
                if profile:
                    Profile.objects.filter(pk=profile.pk).update(
                        postal_code=data["postal_code"],
                        address=data["address"],
                    )
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("user_cart")
        messages.success(request, "سفارش ثبت شد و از موجودی انبار کم شد")
        return redirect("user_orders")

    return render(
        request,
        "user/checkout.html",
        {
            "form": form,
            "cart_items": items,
            "cart_line_count": sum(i.quantity for i in items),
            "cart_total": total,
            "profile": profile,
            "active_nav": "cart",
        },
    )


@staff_required
def staff_dashboard(request):
    order_count = Order.objects.count()
    product_count = Product.objects.filter(is_active=True).count()
    customer_count = Profile.objects.count()
    revenue = Order.objects.exclude(status=OrderStatus.CANCELLED).aggregate(
        total=Sum("total")
    )["total"] or 0
    recent_orders = Order.objects.select_related("user").prefetch_related("items")[:8]
    low_stock_count = sum(
        1 for p in Product.objects.filter(is_active=True).only("stock_kg", "low_stock_kg", "weight")
        if p.is_low_stock
    )
    return render(
        request,
        "staff/dashboard.html",
        {
            "order_count": order_count,
            "product_count": product_count,
            "customer_count": customer_count,
            "revenue": revenue,
            "recent_orders": recent_orders,
            "low_stock_count": low_stock_count,
            "active_nav": "dashboard",
        },
    )


@staff_required
def staff_low_stock(request):
    products = [
        p
        for p in Product.objects.filter(is_active=True)
        .prefetch_related("images")
        .order_by("stock_kg", "name")
        if p.is_low_stock
    ]
    out_count = sum(1 for p in products if p.is_out_of_stock)
    return render(
        request,
        "staff/low_stock.html",
        {
            "products": products,
            "low_stock_count": len(products),
            "out_count": out_count,
            "active_nav": "low_stock",
        },
    )


@staff_required
def staff_orders(request):
    orders = Order.objects.select_related("user").prefetch_related("items")
    return render(
        request,
        "staff/orders.html",
        {
            "orders": orders,
            "active_nav": "orders",
            "status_choices": OrderStatus.choices,
        },
    )


@staff_required
@require_POST
def staff_order_status(request, code):
    order = get_object_or_404(Order, code=code)
    status = request.POST.get("status", "").strip()
    if status not in OrderStatus.values:
        messages.error(request, "وضعیت نامعتبر است")
        return redirect("staff_orders")
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        prev = order.status
        order.status = status
        if status == OrderStatus.CANCELLED and prev != OrderStatus.CANCELLED:
            order.restore_stock()
        order.save(update_fields=["status"])
    messages.success(request, f"وضعیت سفارش {order.code} به‌روز شد")
    return redirect("staff_orders")


@staff_required
def staff_customers(request):
    customers = Profile.objects.select_related("user").annotate(
        order_count=Count("user__orders")
    )
    return render(request, "staff/customers.html", {"customers": customers, "active_nav": "customers"})


@staff_required
def staff_analytics(request):
    by_status = (
        Order.objects.values("status")
        .annotate(count=Count("id"), revenue=Sum("total"))
        .order_by("status")
    )
    top_products = (
        OrderItem.objects.values("product_name")
        .annotate(qty=Sum("quantity"), revenue=Sum(F("unit_price") * F("quantity")))
        .order_by("-qty")[:5]
    )
    return render(
        request,
        "staff/analytics.html",
        {"by_status": by_status, "top_products": top_products, "active_nav": "analytics"},
    )
