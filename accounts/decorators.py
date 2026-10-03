from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect


def customer_required(view_func):
    """Customer-only area: staff are sent to the admin panel."""

    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_staff:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"ok": False, "message": "حساب مدیریت امکان افزودن به سبد ندارد"},
                    status=403,
                )
            messages.info(request, "حساب مدیریت برای خرید مشتری نیست — به پنل ادمین منتقل شدید")
            return redirect("staff_dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def staff_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("دسترسی فقط برای مدیر")
        return view_func(request, *args, **kwargs)

    return _wrapped
