def cart_summary(request):
    if not request.user.is_authenticated:
        return {"cart_count": 0, "cart_total": 0}
    items = request.user.cart_items.select_related("product")
    count = sum(i.quantity for i in items)
    total = sum(i.line_total for i in items)
    return {"cart_count": count, "cart_total": total}
