from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from accounts.decorators import customer_required
from accounts.forms import LoginForm, ProfileForm, SignupForm
from accounts.models import Profile
from accounts.utils import normalize_phone

User = get_user_model()


def _wants_json(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    accept = (request.headers.get("Accept") or "").lower()
    return "application/json" in accept


def _form_errors_payload(form, message=None):
    errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
    first = message
    if not first:
        for key in ("__all__", "phone", "password", "full_name"):
            if key in errors and errors[key]:
                first = errors[key][0]
                break
        if not first:
            for vals in errors.values():
                if vals:
                    first = vals[0]
                    break
    return {
        "ok": False,
        "message": first or "اطلاعات را بررسی کنید",
        "errors": errors,
    }


def _after_login_path(user, next_url=None):
    next_url = str(next_url or "").strip()
    if user.is_staff:
        if next_url.startswith("/staff"):
            return next_url
        return reverse("staff_dashboard")
    if next_url.startswith("/user") or next_url.startswith("/products"):
        return next_url
    return reverse("user_dashboard")


def _after_login_redirect(user, next_url=None):
    """Staff always lands in /staff/; customers in /user/. Ignore next that crosses roles."""
    return redirect(_after_login_path(user, next_url))


@require_http_methods(["GET"])
def auth_go(request):
    """After modal login: send each role to its own panel."""
    if not request.user.is_authenticated:
        return redirect("login")
    return _after_login_redirect(request.user)


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        if _wants_json(request):
            return JsonResponse({"ok": True, "redirect": _after_login_path(request.user)})
        return _after_login_redirect(request.user)
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        user = User.objects.create_user(
            username=phone,
            password=form.cleaned_data["password"],
        )
        Profile.objects.create(
            user=user,
            full_name=form.cleaned_data["full_name"],
            phone=phone,
            city=form.cleaned_data["city"],
            postal_code=form.cleaned_data.get("postal_code") or "",
            address=form.cleaned_data["address"],
        )
        login(request, user)
        messages.success(request, "ثبت‌نام انجام شد")
        path = _after_login_path(user)
        if _wants_json(request):
            return JsonResponse({"ok": True, "redirect": path, "message": "ثبت‌نام انجام شد"})
        return redirect(path)
    if request.method == "POST" and _wants_json(request):
        return JsonResponse(_form_errors_payload(form), status=400)
    return render(request, "storefront/auth.html", {"mode": "signup", "form": form})


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        path = _after_login_path(request.user, request.GET.get("next"))
        if _wants_json(request):
            return JsonResponse({"ok": True, "redirect": path})
        return redirect(path)
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        user = authenticate(
            request,
            username=phone,
            password=form.cleaned_data["password"],
        )
        if user is None:
            form.add_error(None, "شماره یا رمز عبور اشتباه است")
        else:
            login(request, user)
            messages.success(request, "ورود موفق")
            next_url = request.GET.get("next") or request.POST.get("next")
            path = _after_login_path(user, next_url)
            if _wants_json(request):
                return JsonResponse({"ok": True, "redirect": path, "message": "ورود موفق"})
            return redirect(path)
    if request.method == "POST" and _wants_json(request):
        return JsonResponse(
            _form_errors_payload(form, "شماره یا رمز عبور اشتباه است" if form.non_field_errors() else None),
            status=400,
        )
    return render(request, "storefront/auth.html", {"mode": "login", "form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@customer_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or "کاربر رودی",
            "phone": request.user.username,
            "city": "",
            "address": "",
        },
    )
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        if profile.phone != request.user.username:
            request.user.username = profile.phone
            request.user.save(update_fields=["username"])
        messages.success(request, "اطلاعات ذخیره شد")
        return redirect("user_profile")
    return render(request, "user/profile.html", {"form": form, "profile": profile, "active_nav": "profile"})
