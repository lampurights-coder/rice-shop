from django.core.management.base import BaseCommand

from catalog.models import Product

PRODUCTS = [
    {"name": "صدری دم سیاه آستانه اشرفیه", "process": "یک بار الک", "quality": "برنج فوق ممتاز", "stars": 5, "wholesale_price": 590000, "retail_price": 680000, "featured": True, "on_deal": True, "old_retail_price": 790000},
    {"name": "برنج امراللهی کشت دوم", "process": "یک بار الک", "quality": "برنج فوق ممتاز", "stars": 5, "wholesale_price": 480000, "retail_price": 575000, "featured": True, "on_deal": True, "old_retail_price": 690000},
    {"name": "برنج قهوه‌ای فوق ممتاز", "process": "دوبار الک", "quality": "برنج فوق ممتاز", "stars": 4, "wholesale_price": 475000, "retail_price": 548000, "featured": False, "on_deal": False},
    {"name": "برنج طارم هاشمی ممتاز", "process": "یک بار الک", "quality": "برنج ممتاز", "stars": 4, "wholesale_price": 403000, "retail_price": 480000, "featured": True, "on_deal": True, "old_retail_price": 555000},
    {"name": "برنج فجر گرگان", "process": "یک بار الک", "quality": "اقتصادی", "stars": 3, "wholesale_price": 335000, "retail_price": 410000, "featured": False, "on_deal": False},
    {"name": "صدری هاشمی ممتاز ۵ کیلویی", "process": "دوبار الک", "quality": "برنج فوق ممتاز", "stars": 5, "wholesale_price": 620000, "retail_price": 720000, "featured": True, "on_deal": True, "old_retail_price": 860000, "weight": "۵ کیلو"},
    {"name": "صدری دمسیاه فوق ممتاز ۱۰ کیلویی", "process": "یک بار الک", "quality": "برنج فوق ممتاز", "stars": 5, "wholesale_price": 560000, "retail_price": 648000, "featured": True, "on_deal": True, "old_retail_price": 740000, "weight": "۱۰ کیلو"},
    {"name": "برنج هاشمی کشت دوم", "process": "دوبار الک", "quality": "برنج ممتاز", "stars": 4, "wholesale_price": 390000, "retail_price": 465000, "featured": False, "on_deal": False},
    {"name": "برنج عنبربو خوزستان", "process": "یک بار الک", "quality": "برنج ممتاز", "stars": 4, "wholesale_price": 510000, "retail_price": 595000, "featured": False, "on_deal": False},
    {"name": "برنج طارم محلی", "process": "دوبار الک", "quality": "برنج فوق ممتاز", "stars": 5, "wholesale_price": 530000, "retail_price": 610000, "featured": True, "on_deal": False},
    {"name": "برنج اقتصادی خانواده", "process": "یک بار الک", "quality": "اقتصادی", "stars": 3, "wholesale_price": 280000, "retail_price": 345000, "featured": False, "on_deal": False},
    {"name": "برنج صدری گیلان", "process": "دوبار الک", "quality": "برنج ممتاز", "stars": 4, "wholesale_price": 450000, "retail_price": 530000, "featured": False, "on_deal": False},
]


class Command(BaseCommand):
    help = "Seed rice products from storefront catalog"

    def handle(self, *args, **options):
        created = 0
        for row in PRODUCTS:
            _, was_created = Product.objects.update_or_create(
                name=row["name"],
                defaults={
                    "process": row["process"],
                    "quality": row["quality"],
                    "stars": row["stars"],
                    "wholesale_price": row["wholesale_price"],
                    "retail_price": row["retail_price"],
                    "old_retail_price": row.get("old_retail_price"),
                    "featured": row.get("featured", False),
                    "on_deal": row.get("on_deal", False),
                    "weight": row.get("weight", "۵ کیلو"),
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Products ready ({created} new). Total: {Product.objects.count()}"))
