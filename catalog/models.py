from django.db import models
from django.db.models import Q
from django.utils.text import slugify


def customer_public_review_q(prefix=""):
    """Public reviews from customers only (staff/admin scores never inflate the average)."""
    p = prefix
    return Q(**{f"{p}is_public": True}) & (
        Q(**{f"{p}user__isnull": True})
        | (Q(**{f"{p}user__is_staff": False}) & Q(**{f"{p}user__is_superuser": False}))
    )


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    process = models.CharField(max_length=80)
    quality = models.CharField(max_length=80)
    stars = models.PositiveSmallIntegerField(
        default=0,
        help_text="میانگین امتیاز نظرات عمومی (۰ = بدون نظر)",
    )
    wholesale_price = models.PositiveIntegerField()
    retail_price = models.PositiveIntegerField()
    old_retail_price = models.PositiveIntegerField(null=True, blank=True)
    weight = models.CharField(max_length=40, default="۵ کیلو")
    featured = models.BooleanField(default=False)
    on_deal = models.BooleanField(default=False)
    description = models.TextField(blank=True, help_text="متن معرفی زیر عنوان محصول")
    details_text = models.TextField(
        blank=True,
        help_text="متن تب جزئیات (اگر خالی باشد همان توضیحات اصلی استفاده می‌شود)",
    )
    features = models.JSONField(default=list, blank=True, help_text="لیست ویژگی‌ها")
    cook_title = models.CharField(max_length=120, blank=True, default="دستور پخت روی اجاق")
    cook_steps = models.JSONField(default=list, blank=True, help_text="مراحل پخت")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-featured", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True) or "product"
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        return bool(self.old_retail_price and self.old_retail_price > self.retail_price)

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if img:
            return img
        return self.images.first()

    def cover_url(self):
        img = self.primary_image
        if img and img.image:
            return img.image.url
        return None

    def feature_list(self):
        items = self.features if isinstance(self.features, list) else []
        cleaned = [str(x).strip() for x in items if str(x).strip()]
        if cleaned:
            return cleaned
        return [
            "طعم رستورانی و عطر ماندگار",
            "آماده طبخ در حدود ۲۰ دقیقه",
            f"{self.process} — کنترل‌شده کیفیت",
            "مناسب پلو و چلوهای ایرانی",
            "بسته‌بندی بهداشتی و تازه",
            "بدون مواد نگهدارنده",
        ]

    def cook_step_list(self):
        items = self.cook_steps if isinstance(self.cook_steps, list) else []
        cleaned = [str(x).strip() for x in items if str(x).strip()]
        if cleaned:
            return cleaned
        return [
            "برنج را بشویید و در قابلمه سنگین با کمی روغن یا کره روی حرارت متوسط ۲ دقیقه تفت دهید.",
            "حدود ۲٫۵ پیمانه آب اضافه کنید، هم بزنید و بگذارید به جوش بیاید.",
            "حرارت را کم کنید و حدود ۲۰ دقیقه بدون درب بجوشد تا دانه‌ها نرم شوند.",
            "در صورت تمایل با کمی کره یا سبزی تازه تزئین کنید و داغ سرو نمایید.",
        ]

    def details_paragraph(self):
        return (self.details_text or self.description or "").strip()

    def public_reviews(self):
        """Customer-facing reviews (excludes staff/admin authors)."""
        return self.reviews.filter(customer_public_review_q())

    def review_stats(self, *, fresh=False):
        """Average of public customer reviews. Use fresh=True to ignore list-query annotations."""
        from django.db.models import Avg

        if (
            not fresh
            and hasattr(self, "review_count_ann")
            and self.review_count_ann is not None
        ):
            count = int(self.review_count_ann or 0)
            avg = float(self.review_avg_ann or 0) if count else 0.0
        else:
            qs = self.public_reviews()
            count = qs.count()
            avg = float(qs.aggregate(a=Avg("stars"))["a"] or 0) if count else 0.0

        if not count:
            return {"count": 0, "avg": 0.0, "avg_text": "", "has_reviews": False}

        avg = round(avg, 1)
        avg_text = f"{avg:.1f}".replace(".", "٫")
        return {"count": count, "avg": avg, "avg_text": avg_text, "has_reviews": True}

    def sync_rating_from_reviews(self):
        """Keep Product.stars in sync with public review average; return fresh stats."""
        stats = self.review_stats(fresh=True)
        new_stars = int(round(stats["avg"])) if stats["has_reviews"] else 0
        new_stars = max(0, min(5, new_stars))
        if self.stars != new_stars:
            Product.objects.filter(pk=self.pk).update(stars=new_stars)
            self.stars = new_stars
        # Drop stale list annotations so later .review_stats() is correct
        for attr in ("review_count_ann", "review_avg_ann"):
            if hasattr(self, attr):
                try:
                    delattr(self, attr)
                except AttributeError:
                    pass
        return stats


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "sort_order", "id"]

    def __str__(self):
        return f"{self.product_id} image {self.pk}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_reviews",
    )
    author_name = models.CharField(max_length=80)
    title = models.CharField(max_length=80)
    body = models.TextField(max_length=500)
    stars = models.PositiveSmallIntegerField(default=5)
    verified = models.BooleanField(default=False)
    reply_body = models.TextField(blank=True)
    reply_name = models.CharField(max_length=80, blank=True, default="برنج رودی")
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_id}: {self.title}"

    @property
    def has_reply(self):
        return bool((self.reply_body or "").strip())

    @property
    def needs_reply(self):
        return not self.has_reply


class SiteSettings(models.Model):
    """Singleton storefront contact / about content (editable in staff panel)."""

    singleton_id = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    brand_name = models.CharField(max_length=80, default="برنج رودی")
    footer_tagline = models.CharField(
        max_length=200,
        default="برنج طبیعی ممتاز برای سفره‌های ایرانی.",
    )
    about_title = models.CharField(
        max_length=160,
        default="کارخانه تخصصی برنج ایرانی به تمام عیار",
    )
    about_body = models.TextField(
        blank=True,
        default="ما متعهدیم بهترین برنج طبیعی را با کیفیت ثابت و طعمی ماندگار به سفره شما برسانیم.",
    )
    phone_numbers = models.JSONField(
        default=list,
        blank=True,
        help_text="لیست شماره تماس‌ها",
    )
    working_hours = models.CharField(
        max_length=220,
        default="ساعات کاری شنبه تا پنجشنبه از ۹ الی ۱۸ و پشتیبانی آنلاین ۹ الی ۲۳",
    )
    factory_line = models.CharField(
        max_length=200,
        default="کارخانه تخصصی برنج ایرانی به تمام عیار",
        blank=True,
    )
    address_hq = models.TextField(
        default="تهران – جنوب به شمال بزرگراه نواب – لاین کندرو جوادیه – کوچه نظری ۱۲۱ – پلاک ۱۲ – ساختمان برنج آنلاین",
    )
    address_processing = models.TextField(
        default="تهران - بزرگراه شهید چراغی - مجتمع تجاری پردیس کیان - واحد ۱۲۰",
        blank=True,
    )
    email = models.EmailField(default="info@riceonline.ir")

    # Homepage hero
    hero_title = models.CharField(max_length=120, default="برنج طبیعی ممتاز")
    hero_subtitle = models.CharField(max_length=160, default="برای سفره‌های سالم‌تر")
    hero_lead = models.TextField(
        default="برنج ۱۰۰٪ طبیعی و مغذی برای آشپزی خانگی و حرفه‌ای. انتخاب مطمئن هزاران خانواده در سراسر کشور.",
    )
    hero_primary_btn = models.CharField(max_length=60, default="خرید کنید")
    hero_secondary_btn = models.CharField(max_length=60, default="تماس با ما")
    stat1_value = models.PositiveIntegerField(default=100)
    stat1_suffix = models.CharField(max_length=20, default="هزار+", blank=True)
    stat1_label = models.CharField(max_length=60, default="کشاورز همکار")
    stat2_value = models.PositiveIntegerField(default=25)
    stat2_suffix = models.CharField(max_length=20, default="%", blank=True)
    stat2_label = models.CharField(max_length=60, default="کیفیت بالاتر")
    stat3_value = models.PositiveIntegerField(default=100)
    stat3_suffix = models.CharField(max_length=20, default="%", blank=True)
    stat3_label = models.CharField(max_length=60, default="طبیعی")

    # Homepage CTA band
    cta_title = models.CharField(max_length=160, default="آماده خرید برنج ممتاز هستید؟")
    cta_body = models.CharField(
        max_length=240,
        default="انواع برنج طبیعی را ببینید و سفارش خود را همین حالا ثبت کنید.",
    )
    cta_button = models.CharField(max_length=60, default="مشاهده محصولات")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات فروشگاه"
        verbose_name_plural = "تنظیمات فروشگاه"

    def __str__(self):
        return self.brand_name or "تنظیمات فروشگاه"

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)

    @classmethod
    def defaults(cls):
        return {
            "brand_name": "برنج رودی",
            "footer_tagline": "برنج طبیعی ممتاز برای سفره‌های ایرانی.",
            "about_title": "کارخانه تخصصی برنج ایرانی به تمام عیار",
            "about_body": "ما متعهدیم بهترین برنج طبیعی را با کیفیت ثابت و طعمی ماندگار به سفره شما برسانیم.",
            "phone_numbers": ["02155680957", "02155680678", "02155680696"],
            "working_hours": "ساعات کاری شنبه تا پنجشنبه از ۹ الی ۱۸ و پشتیبانی آنلاین ۹ الی ۲۳",
            "factory_line": "کارخانه تخصصی برنج ایرانی به تمام عیار",
            "address_hq": "تهران – جنوب به شمال بزرگراه نواب – لاین کندرو جوادیه – کوچه نظری ۱۲۱ – پلاک ۱۲ – ساختمان برنج آنلاین",
            "address_processing": "تهران - بزرگراه شهید چراغی - مجتمع تجاری پردیس کیان - واحد ۱۲۰",
            "email": "info@riceonline.ir",
            "hero_title": "برنج طبیعی ممتاز",
            "hero_subtitle": "برای سفره‌های سالم‌تر",
            "hero_lead": "برنج ۱۰۰٪ طبیعی و مغذی برای آشپزی خانگی و حرفه‌ای. انتخاب مطمئن هزاران خانواده در سراسر کشور.",
            "hero_primary_btn": "خرید کنید",
            "hero_secondary_btn": "تماس با ما",
            "stat1_value": 100,
            "stat1_suffix": "هزار+",
            "stat1_label": "کشاورز همکار",
            "stat2_value": 25,
            "stat2_suffix": "%",
            "stat2_label": "کیفیت بالاتر",
            "stat3_value": 100,
            "stat3_suffix": "%",
            "stat3_label": "طبیعی",
            "cta_title": "آماده خرید برنج ممتاز هستید؟",
            "cta_body": "انواع برنج طبیعی را ببینید و سفارش خود را همین حالا ثبت کنید.",
            "cta_button": "مشاهده محصولات",
        }

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(singleton_id=1, defaults=cls.defaults())
        if created:
            return obj
        # Fill empty phone list once for existing rows
        if not obj.phone_numbers:
            obj.phone_numbers = cls.defaults()["phone_numbers"]
            obj.save(update_fields=["phone_numbers"])
        return obj

    @property
    def phone_list(self):
        raw = self.phone_numbers or []
        if isinstance(raw, str):
            raw = [raw]
        return [str(p).strip() for p in raw if str(p).strip()]

    @property
    def phones_display(self):
        return " - ".join(self.phone_list)
