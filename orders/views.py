from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.decorators import customer_required, staff_required
from accounts.models import Profile
from accounts.utils import get_user_profile
from catalog.models import Product
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
    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status"])
    messages.success(request, "سفارش لغو شد")
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
    if not created:
        item.quantity += qty
    else:
        item.quantity = qty
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
        item.quantity = max(1, item.quantity + delta)
        item.save()
    return redirect("user_cart")


@customer_required
@require_POST
def checkout_view(request):
    items = list(_cart_items(request.user))
    if not items:
        messages.error(request, "سبد خرید خالی است")
        return redirect("user_cart")
    total = sum(i.line_total for i in items)
    order = Order.objects.create(user=request.user, code=Order.generate_code(), total=total)
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            weight=item.product.weight,
            quantity=item.quantity,
            unit_price=item.product.retail_price,
        )
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "سفارش ثبت شد")
    return redirect("user_orders")


@staff_required
def staff_dashboard(request):
    order_count = Order.objects.count()
    product_count = Product.objects.filter(is_active=True).count()
    customer_count = Profile.objects.count()
    revenue = Order.objects.exclude(status=OrderStatus.CANCELLED).aggregate(
        total=Sum("total")
    )["total"] or 0
    recent_orders = Order.objects.select_related("user").prefetch_related("items")[:8]
    return render(
        request,
        "staff/dashboard.html",
        {
            "order_count": order_count,
            "product_count": product_count,
            "customer_count": customer_count,
            "revenue": revenue,
            "recent_orders": recent_orders,
            "active_nav": "dashboard",
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
    order.status = status
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
