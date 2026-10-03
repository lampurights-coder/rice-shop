from django import forms
from django.contrib.auth import get_user_model

from accounts.models import Profile
from accounts.utils import normalize_phone, valid_phone

User = get_user_model()


class SignupForm(forms.Form):
    full_name = forms.CharField(
        max_length=120,
        label="نام و نام خانوادگی",
        error_messages={"required": "نام و نام خانوادگی را وارد کنید"},
    )
    phone = forms.CharField(
        max_length=11,
        label="موبایل",
        error_messages={"required": "شماره موبایل را وارد کنید"},
    )
    city = forms.CharField(
        max_length=80,
        label="شهر",
        error_messages={"required": "شهر را وارد کنید"},
    )
    postal_code = forms.CharField(max_length=10, required=False, label="کد پستی")
    address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        label="آدرس",
        error_messages={"required": "آدرس را وارد کنید"},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=6,
        label="رمز عبور",
        error_messages={
            "required": "رمز عبور را وارد کنید",
            "min_length": "رمز عبور باید حداقل ۶ کاراکتر باشد",
        },
    )

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if not valid_phone(phone):
            raise forms.ValidationError("شماره موبایل معتبر وارد کنید")
        if User.objects.filter(username=phone).exists():
            raise forms.ValidationError("این شماره قبلاً ثبت شده است")
        return phone

    def clean_postal_code(self):
        postal = (self.cleaned_data.get("postal_code") or "").strip()
        if postal and (len(postal) != 10 or not postal.isdigit()):
            raise forms.ValidationError("کد پستی باید ۱۰ رقم باشد")
        return postal


class LoginForm(forms.Form):
    phone = forms.CharField(
        max_length=11,
        label="موبایل",
        error_messages={"required": "شماره موبایل را وارد کنید"},
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="رمز عبور",
        error_messages={"required": "رمز عبور را وارد کنید"},
    )

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if not valid_phone(phone):
            raise forms.ValidationError("شماره موبایل معتبر وارد کنید")
        return phone


_INPUT = {}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "phone", "city", "postal_code", "address"]
        labels = {
            "full_name": "نام و نام خانوادگی",
            "phone": "موبایل",
            "city": "شهر",
            "postal_code": "کد پستی",
            "address": "آدرس",
        }
        widgets = {
            "full_name": forms.TextInput(attrs=_INPUT),
            "phone": forms.TextInput(attrs={**_INPUT, "dir": "ltr"}),
            "city": forms.TextInput(attrs=_INPUT),
            "postal_code": forms.TextInput(attrs={**_INPUT, "dir": "ltr"}),
            "address": forms.Textarea(attrs={**_INPUT, "rows": 3}),
        }

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if not valid_phone(phone):
            raise forms.ValidationError("شماره موبایل معتبر وارد کنید")
        qs = Profile.objects.filter(phone=phone).exclude(user=self.instance.user)
        if qs.exists():
            raise forms.ValidationError("این شماره برای حساب دیگری ثبت شده")
        return phone
