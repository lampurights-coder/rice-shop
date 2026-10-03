from django import template
from django.templatetags.static import static

register = template.Library()

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


@register.filter
def fa_digits(value):
    """Convert Western digits in a string/number to Persian digits."""
    return str(value).translate(_FA_DIGITS)


@register.filter
def fa_number(value):
    try:
        return f"{int(value):,}".replace(",", "٬").translate(_FA_DIGITS)
    except (TypeError, ValueError):
        return value


@register.filter
def money(value):
    try:
        n = int(value)
        return f"{n:,}".replace(",", "٬").translate(_FA_DIGITS) + " تومان"
    except (TypeError, ValueError):
        return value


@register.filter
def product_cover(product):
    """Primary product image URL, or default rice image."""
    try:
        url = product.cover_url()
        if url:
            return url
    except Exception:
        pass
    return static("img/berenj.webp")


@register.filter
def stars_html(n):
    try:
        n = int(round(float(n)))
    except (TypeError, ValueError):
        n = 0
    n = max(0, min(5, n))
    if n <= 0:
        return ""
    html = ""
    for i in range(1, 6):
        cls = "is-on" if i <= n else ""
        html += f'<span class="{cls}">★</span>'
    return html


@register.filter
def star_glyphs(n):
    try:
        n = int(round(float(n)))
    except (TypeError, ValueError):
        n = 0
    n = max(0, min(5, n))
    return ("★" * n) + ("☆" * (5 - n))
