import re

from django import forms
from django.utils import timezone

_FA_TO_EN = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
_INPUT = {"class": "field-input"}
_TEXTAREA = {"class": "field-input", "rows": 3}


class CheckoutForm(forms.Form):
    delivery_date = forms.DateField(
        label="تاریخ تحویل",
        widget=forms.DateInput(attrs={**_INPUT, "type": "date", "dir": "ltr"}),
    )
    postal_code = forms.CharField(
        label="کد پستی",
        max_length=10,
        widget=forms.TextInput(
            attrs={
                **_INPUT,
                "dir": "ltr",
                "inputmode": "numeric",
                "placeholder": "۱۲۳۴۵۶۷۸۹۰",
                "autocomplete": "postal-code",
            }
        ),
    )
    address = forms.CharField(
        label="آدرس کامل ارسال",
        widget=forms.Textarea(
            attrs={
                **_TEXTAREA,
                "placeholder": "استان، شهر، خیابان، پلاک، واحد…",
                "autocomplete": "street-address",
            }
        ),
    )

    def clean_postal_code(self):
        raw = (self.cleaned_data.get("postal_code") or "").translate(_FA_TO_EN)
        digits = re.sub(r"\D", "", raw)
        if len(digits) != 10:
            raise forms.ValidationError("کد پستی باید ۱۰ رقم باشد")
        return digits

    def clean_address(self):
        address = (self.cleaned_data.get("address") or "").strip()
        if len(address) < 8:
            raise forms.ValidationError("آدرس را کامل‌تر وارد کنید")
        return address

    def clean_delivery_date(self):
        day = self.cleaned_data.get("delivery_date")
        if day and day < timezone.localdate():
            raise forms.ValidationError("تاریخ تحویل نمی‌تواند در گذشته باشد")
        return day
