from django import forms

from catalog.models import Product, ProductReview, SiteSettings

PROCESS_CHOICES = [
    ("یک بار الک", "یک بار الک"),
    ("دوبار الک", "دوبار الک"),
]

QUALITY_CHOICES = [
    ("برنج فوق ممتاز", "برنج فوق ممتاز"),
    ("برنج ممتاز", "برنج ممتاز"),
    ("اقتصادی", "اقتصادی"),
]

WEIGHT_CHOICES = [
    ("۵ کیلو", "۵ کیلو"),
    ("۱۰ کیلو", "۱۰ کیلو"),
    ("۱ کیلو", "۱ کیلو"),
]

_INPUT = {"class": "staff-input"}
_SELECT = {"class": "staff-select"}
_TEXTAREA = {"class": "staff-textarea", "rows": 4}
_CHECK = {"class": "staff-check-input"}


class ProductForm(forms.ModelForm):
    process = forms.ChoiceField(
        choices=PROCESS_CHOICES,
        label="نوع فرآوری",
        initial="یک بار الک",
        widget=forms.Select(attrs=_SELECT),
    )
    quality = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        label="نوع برنج / کیفیت",
        initial="برنج ممتاز",
        widget=forms.Select(attrs=_SELECT),
    )
    weight = forms.ChoiceField(
        choices=WEIGHT_CHOICES,
        label="وزن بسته‌بندی",
        initial="۵ کیلو",
        widget=forms.Select(attrs=_SELECT),
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "process",
            "quality",
            "weight",
            "wholesale_price",
            "retail_price",
            "old_retail_price",
            "description",
            "featured",
            "on_deal",
            "is_active",
        ]
        labels = {
            "name": "نام محصول",
            "wholesale_price": "قیمت عمده (تومان)",
            "retail_price": "قیمت جزئی (تومان)",
            "old_retail_price": "قیمت قبلی / قبل از تخفیف (تومان)",
            "description": "توضیحات محصول",
            "featured": "پرفروش / ویژه",
            "on_deal": "نمایش در تخفیفی‌ها",
            "is_active": "فعال در فروشگاه",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={**_INPUT, "placeholder": "مثلاً: صدری دم‌سیاه آستانه", "autocomplete": "off"}
            ),
            "wholesale_price": forms.NumberInput(
                attrs={**_INPUT, "min": 0, "dir": "ltr", "placeholder": "۴۵۰۰۰۰"}
            ),
            "retail_price": forms.NumberInput(
                attrs={**_INPUT, "min": 0, "dir": "ltr", "placeholder": "۵۲۰۰۰۰"}
            ),
            "old_retail_price": forms.NumberInput(
                attrs={**_INPUT, "min": 0, "dir": "ltr", "placeholder": "اختیاری"}
            ),
            "description": forms.Textarea(
                attrs={
                    **_TEXTAREA,
                    "rows": 5,
                    "placeholder": "متن معرفی محصول برای صفحه فروشگاه…",
                }
            ),
            "featured": forms.CheckboxInput(attrs=_CHECK),
            "on_deal": forms.CheckboxInput(attrs=_CHECK),
            "is_active": forms.CheckboxInput(attrs=_CHECK),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_retail_price"].required = False
        self.fields["description"].required = False
        self.fields["featured"].required = False
        self.fields["on_deal"].required = False
        self.fields["is_active"].required = False
        if not self.instance.pk:
            self.fields["is_active"].initial = True
            self.fields["process"].initial = "یک بار الک"
            self.fields["quality"].initial = "برنج ممتاز"
            self.fields["weight"].initial = "۵ کیلو"

    def save(self, commit=True):
        product = super().save(commit=False)
        if not product.pk:
            product.stars = 0
        if commit:
            product.save()
            self.save_m2m()
        return product

    def clean_old_retail_price(self):
        value = self.cleaned_data.get("old_retail_price")
        if value in (None, ""):
            return None
        return value


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["author_name", "title", "body", "stars"]
        labels = {
            "author_name": "نام شما",
            "title": "عنوان",
            "body": "متن نظر",
            "stars": "امتیاز",
        }
        widgets = {
            "author_name": forms.TextInput(
                attrs={"id": "review-name", "maxlength": 80, "placeholder": "مثلاً: سارا م.", "required": True}
            ),
            "title": forms.TextInput(
                attrs={"id": "review-title", "maxlength": 80, "placeholder": "مثلاً: عطر عالی", "required": True}
            ),
            "body": forms.Textarea(
                attrs={
                    "id": "review-body",
                    "rows": 4,
                    "maxlength": 500,
                    "placeholder": "تجربه‌تان از این برنج را بنویسید...",
                    "required": True,
                }
            ),
            "stars": forms.NumberInput(attrs={"id": "review-stars", "min": 1, "max": 5, "value": 5}),
        }

    def clean_stars(self):
        stars = self.cleaned_data["stars"]
        if stars < 1 or stars > 5:
            raise forms.ValidationError("امتیاز باید بین ۱ و ۵ باشد")
        return stars


class SiteSettingsForm(forms.ModelForm):
    phone_numbers_text = forms.CharField(
        label="شماره‌های تماس",
        required=False,
        widget=forms.Textarea(
            attrs={
                **_TEXTAREA,
                "rows": 4,
                "placeholder": "هر شماره در یک خط\n02155680957\n02155680678",
                "dir": "ltr",
            }
        ),
        help_text="هر شماره را در یک خط جدا بنویسید. می‌توانید چند شماره ثبت کنید.",
    )

    class Meta:
        model = SiteSettings
        fields = [
            "brand_name",
            "footer_tagline",
            "hero_title",
            "hero_subtitle",
            "hero_lead",
            "hero_primary_btn",
            "hero_secondary_btn",
            "stat1_value",
            "stat1_suffix",
            "stat1_label",
            "stat2_value",
            "stat2_suffix",
            "stat2_label",
            "stat3_value",
            "stat3_suffix",
            "stat3_label",
            "cta_title",
            "cta_body",
            "cta_button",
            "factory_line",
            "working_hours",
            "address_hq",
            "address_processing",
            "email",
        ]
        labels = {
            "brand_name": "نام برند",
            "footer_tagline": "متن کوتاه پاورقی",
            "hero_title": "عنوان اصلی صفحه اول",
            "hero_subtitle": "زیرعنوان صفحه اول",
            "hero_lead": "توضیح کوتاه صفحه اول",
            "hero_primary_btn": "دکمه اصلی",
            "hero_secondary_btn": "دکمه دوم",
            "stat1_value": "آمار ۱ — عدد",
            "stat1_suffix": "آمار ۱ — پسوند",
            "stat1_label": "آمار ۱ — برچسب",
            "stat2_value": "آمار ۲ — عدد",
            "stat2_suffix": "آمار ۲ — پسوند",
            "stat2_label": "آمار ۲ — برچسب",
            "stat3_value": "آمار ۳ — عدد",
            "stat3_suffix": "آمار ۳ — پسوند",
            "stat3_label": "آمار ۳ — برچسب",
            "cta_title": "عنوان بخش دعوت به خرید",
            "cta_body": "متن بخش دعوت به خرید",
            "cta_button": "متن دکمه دعوت به خرید",
            "factory_line": "معرفی کارخانه",
            "working_hours": "ساعات کاری",
            "address_hq": "آدرس دفتر مرکزی",
            "address_processing": "آدرس واحد پردازش",
            "email": "ایمیل",
        }
        widgets = {
            "brand_name": forms.TextInput(attrs=_INPUT),
            "footer_tagline": forms.TextInput(attrs=_INPUT),
            "hero_title": forms.TextInput(attrs=_INPUT),
            "hero_subtitle": forms.TextInput(attrs=_INPUT),
            "hero_lead": forms.Textarea(attrs={**_TEXTAREA, "rows": 3}),
            "hero_primary_btn": forms.TextInput(attrs=_INPUT),
            "hero_secondary_btn": forms.TextInput(attrs=_INPUT),
            "stat1_value": forms.NumberInput(attrs={**_INPUT, "min": 0}),
            "stat1_suffix": forms.TextInput(attrs=_INPUT),
            "stat1_label": forms.TextInput(attrs=_INPUT),
            "stat2_value": forms.NumberInput(attrs={**_INPUT, "min": 0}),
            "stat2_suffix": forms.TextInput(attrs=_INPUT),
            "stat2_label": forms.TextInput(attrs=_INPUT),
            "stat3_value": forms.NumberInput(attrs={**_INPUT, "min": 0}),
            "stat3_suffix": forms.TextInput(attrs=_INPUT),
            "stat3_label": forms.TextInput(attrs=_INPUT),
            "cta_title": forms.TextInput(attrs=_INPUT),
            "cta_body": forms.TextInput(attrs=_INPUT),
            "cta_button": forms.TextInput(attrs=_INPUT),
            "factory_line": forms.TextInput(attrs=_INPUT),
            "working_hours": forms.TextInput(attrs=_INPUT),
            "address_hq": forms.Textarea(attrs={**_TEXTAREA, "rows": 3}),
            "address_processing": forms.Textarea(attrs={**_TEXTAREA, "rows": 3}),
            "email": forms.EmailInput(attrs={**_INPUT, "dir": "ltr"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        phones = []
        if self.instance and self.instance.pk:
            phones = self.instance.phone_list
        self.fields["phone_numbers_text"].initial = "\n".join(phones)

    def clean_phone_numbers_text(self):
        text = self.cleaned_data.get("phone_numbers_text") or ""
        for sep in (" - ", " – ", " — ", "،", ","):
            text = text.replace(sep, "\n")
        phones = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                phones.append(line)
        return phones

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.phone_numbers = self.cleaned_data.get("phone_numbers_text") or []
        if commit:
            obj.save()
        return obj
