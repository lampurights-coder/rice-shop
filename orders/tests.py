from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Profile
from catalog.models import Product
from orders.models import CartItem, Order, OrderStatus

User = get_user_model()


class ShopTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="برنج طارم هاشمی",
            process="یک بار الک",
            quality="برنج ممتاز",
            stars=4,
            wholesale_price=403000,
            retail_price=480000,
            featured=True,
        )
        self.customer = User.objects.create_user(username="09121234567", password="secret12")
        Profile.objects.create(
            user=self.customer,
            full_name="کاربر تست",
            phone="09121234567",
            city="رشت",
            postal_code="4136745890",
            address="خیابان تست",
        )
        self.staff = User.objects.create_user(
            username="09129876543",
            password="staffpass1",
            is_staff=True,
        )

    def test_storefront_pages_anonymous(self):
        for name in ("home", "product_list", "product_detail"):
            url = reverse(name, args=() if name != "product_detail" else (self.product.pk,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            if name == "product_list":
                self.assertContains(response, self.product.name)

    def test_product_search_and_legacy_url(self):
        hit = self.client.get(reverse("product_list"), {"q": "هاشمی"})
        self.assertEqual(hit.status_code, 200)
        self.assertContains(hit, self.product.name)
        miss = self.client.get(reverse("product_list"), {"q": "zzzz-no-match"})
        self.assertEqual(miss.status_code, 200)
        self.assertContains(miss, "پیدا نشد")
        legacy = self.client.get("/products.html", {"q": "هاشمی"})
        self.assertEqual(legacy.status_code, 302)
        self.assertIn("/products/", legacy.url)
        self.assertIn("q=", legacy.url)

    def test_live_search_api(self):
        response = self.client.get(reverse("product_search_api"), {"q": "هاشمی"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], self.product.name)
        self.assertIn("/products/", data["results"][0]["url"])

    def test_signup_creates_user_and_profile(self):
        response = self.client.post(
            reverse("signup"),
            {
                "full_name": "علی جدید",
                "phone": "09131112233",
                "city": "تهران",
                "postal_code": "1234567890",
                "address": "خیابان جدید",
                "password": "newpass1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="09131112233").exists())
        user = User.objects.get(username="09131112233")
        self.assertEqual(user.profile.full_name, "علی جدید")

    def test_login_redirects_to_user_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"phone": "09121234567", "password": "secret12"},
        )
        self.assertRedirects(response, reverse("user_dashboard"))

    def test_login_json_wrong_password_persian(self):
        response = self.client.post(
            reverse("login"),
            {"phone": "09121234567", "password": "wrongpass"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertIn("اشتباه", data["message"])

    def test_signup_json_short_password_persian(self):
        response = self.client.post(
            reverse("signup"),
            {
                "full_name": "تست کوتاه",
                "phone": "09139998877",
                "city": "رشت",
                "postal_code": "",
                "address": "آدرس تست",
                "password": "123",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["ok"])
        self.assertIn("۶", data["errors"]["password"][0])

    def test_staff_login_goes_to_staff_not_user(self):
        response = self.client.post(
            reverse("login"),
            {"phone": "09129876543", "password": "staffpass1"},
        )
        self.assertRedirects(response, reverse("staff_dashboard"))
        # user panel redirects staff away
        response = self.client.get(reverse("user_dashboard"))
        self.assertRedirects(response, reverse("staff_dashboard"))
        # logout works
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_staff_cannot_use_cart(self):
        self.client.login(username="09129876543", password="staffpass1")
        cart = self.client.get(reverse("user_cart"))
        self.assertRedirects(cart, reverse("staff_dashboard"))
        add = self.client.post(reverse("cart_add", args=(self.product.pk,)), {"quantity": 1})
        self.assertRedirects(add, reverse("staff_dashboard"))
        self.assertEqual(CartItem.objects.filter(user=self.staff).count(), 0)
        orders = self.client.get(reverse("user_orders"))
        self.assertRedirects(orders, reverse("staff_dashboard"))
        profile = self.client.get(reverse("user_profile"))
        self.assertRedirects(profile, reverse("staff_dashboard"))

    def test_cart_add_update_checkout(self):
        self.client.login(username="09121234567", password="secret12")
        add_url = reverse("cart_add", args=(self.product.pk,))
        self.client.post(add_url, {"quantity": 2})
        self.assertEqual(CartItem.objects.get(user=self.customer).quantity, 2)

        item = CartItem.objects.get(user=self.customer)
        self.client.post(reverse("cart_update", args=(item.id,)), {"delta": 1})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

        self.client.post(reverse("checkout"))
        self.assertEqual(Order.objects.filter(user=self.customer).count(), 1)
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)
        order = Order.objects.get(user=self.customer)
        self.assertEqual(order.total, 480000 * 3)

    def test_cart_remove(self):
        self.client.login(username="09121234567", password="secret12")
        self.client.post(reverse("cart_add", args=(self.product.pk,)), {"quantity": 1})
        item = CartItem.objects.get(user=self.customer)
        self.client.post(reverse("cart_update", args=(item.id,)), {"action": "remove"})
        self.assertEqual(CartItem.objects.filter(user=self.customer).count(), 0)

    def test_cancel_processing_order(self):
        self.client.login(username="09121234567", password="secret12")
        order = Order.objects.create(
            user=self.customer,
            code="ORD-TEST-001",
            status=OrderStatus.PROCESSING,
            total=480000,
        )
        response = self.client.post(reverse("order_cancel", args=(order.code,)))
        self.assertRedirects(response, reverse("user_orders"))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_cannot_cancel_shipped_order(self):
        self.client.login(username="09121234567", password="secret12")
        order = Order.objects.create(
            user=self.customer,
            code="ORD-TEST-002",
            status=OrderStatus.SHIPPED,
            total=480000,
        )
        self.client.post(reverse("order_cancel", args=(order.code,)))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.SHIPPED)

    def test_profile_update(self):
        self.client.login(username="09121234567", password="secret12")
        response = self.client.post(
            reverse("user_profile"),
            {
                "full_name": "نام جدید",
                "phone": "09121234567",
                "city": "اصفهان",
                "postal_code": "8134567890",
                "address": "آدرس جدید",
            },
        )
        self.assertRedirects(response, reverse("user_profile"))
        self.customer.profile.refresh_from_db()
        self.assertEqual(self.customer.profile.city, "اصفهان")
        self.assertEqual(self.customer.profile.full_name, "نام جدید")

    def test_staff_can_access_admin_pages(self):
        self.client.login(username="09129876543", password="staffpass1")
        for name in (
            "staff_dashboard",
            "staff_orders",
            "staff_products",
            "staff_customers",
            "staff_analytics",
            "staff_product_create",
        ):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_staff_product_create_edit_delete(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from catalog.models import ProductImage

        self.client.login(username="09129876543", password="staffpass1")
        tiny = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
            b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00"
            b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        img1 = SimpleUploadedFile("a.gif", tiny, content_type="image/gif")
        img2 = SimpleUploadedFile("b.gif", tiny, content_type="image/gif")
        create = self.client.post(
            reverse("staff_product_create"),
            {
                "name": "برنج تست ادمین",
                "process": "یک بار الک",
                "quality": "برنج ممتاز",
                "weight": "۵ کیلو",
                "stars": 5,
                "wholesale_price": 400000,
                "retail_price": 450000,
                "old_retail_price": "",
                "description": "توضیح تست",
                "featured": "on",
                "on_deal": "on",
                "is_active": "on",
                "images": [img1, img2],
                "primary_new": "1",
            },
        )
        product = Product.objects.get(name="برنج تست ادمین")
        self.assertRedirects(create, reverse("staff_product_edit", args=(product.pk,)))
        self.assertTrue(product.featured)
        self.assertTrue(product.on_deal)
        self.assertEqual(ProductImage.objects.filter(product=product).count(), 2)
        self.assertTrue(ProductImage.objects.filter(product=product, is_primary=True).exists())
        primary = ProductImage.objects.get(product=product, is_primary=True)
        self.assertTrue(primary.image.name.split("/")[-1].startswith("b"))

        # step-by-step AJAX image add
        img3 = SimpleUploadedFile("c.gif", tiny, content_type="image/gif")
        add = self.client.post(
            reverse("staff_product_image_add", args=(product.pk,)),
            {"image": img3, "make_primary": "1"},
        )
        self.assertEqual(add.status_code, 200)
        self.assertTrue(add.json()["ok"])
        self.assertEqual(ProductImage.objects.filter(product=product).count(), 3)
        self.assertTrue(
            ProductImage.objects.get(product=product, is_primary=True).image.name.split("/")[-1].startswith("c")
        )

        edit = self.client.post(
            reverse("staff_product_edit", args=(product.pk,)),
            {
                "name": "برنج تست ویرایش",
                "process": "دوبار الک",
                "quality": "اقتصادی",
                "weight": "۱۰ کیلو",
                "stars": 3,
                "wholesale_price": 300000,
                "retail_price": 350000,
                "old_retail_price": 400000,
                "description": "ویرایش شد",
                "details_text": "متن تب جزئیات",
                "features": ["ویژگی یک", "ویژگی دو"],
                "cook_title": "دستور پخت تست",
                "cook_steps": ["مرحله یک", "مرحله دو"],
                "is_active": "on",
            },
        )
        self.assertRedirects(edit, reverse("staff_product_edit", args=(product.pk,)))
        product.refresh_from_db()
        self.assertEqual(product.name, "برنج تست ویرایش")
        self.assertEqual(product.retail_price, 350000)
        self.assertFalse(product.featured)
        self.assertEqual(product.details_text, "متن تب جزئیات")
        self.assertEqual(product.features, ["ویژگی یک", "ویژگی دو"])
        self.assertEqual(product.cook_title, "دستور پخت تست")
        self.assertEqual(product.cook_steps, ["مرحله یک", "مرحله دو"])
        detail = self.client.get(reverse("product_detail", args=(product.pk,)))
        self.assertContains(detail, "ویژگی یک")
        self.assertContains(detail, "مرحله دو")
        self.assertContains(detail, "دستور پخت تست")

        delete = self.client.post(reverse("staff_product_delete", args=(product.pk,)))
        self.assertRedirects(delete, reverse("staff_products"))
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_staff_can_update_order_status(self):
        self.client.login(username="09121234567", password="secret12")
        self.client.post(reverse("cart_add", args=(self.product.pk,)), {"quantity": 1})
        self.client.post(reverse("checkout"))
        order = Order.objects.get(user=self.customer)

        self.client.logout()
        self.client.login(username="09129876543", password="staffpass1")
        response = self.client.post(
            reverse("staff_order_status", args=(order.code,)),
            {"status": OrderStatus.SHIPPED},
        )
        self.assertRedirects(response, reverse("staff_orders"))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.SHIPPED)

    def test_customer_cannot_access_staff_pages(self):
        self.client.login(username="09121234567", password="secret12")
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_empty_checkout_redirects(self):
        self.client.login(username="09121234567", password="secret12")
        response = self.client.post(reverse("checkout"))
        self.assertRedirects(response, reverse("user_cart"))
        self.assertEqual(Order.objects.filter(user=self.customer).count(), 0)

    def test_user_pages_require_login(self):
        for name in ("user_dashboard", "user_cart", "user_orders", "user_profile"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/auth/login/", response.url)

    def test_user_dashboard_without_profile(self):
        bare = User.objects.create_user(username="09125556677", password="secret12")
        self.client.login(username="09125556677", password="secret12")
        response = self.client.get(reverse("user_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_product_review_create(self):
        from catalog.models import ProductReview

        response = self.client.post(
            reverse("product_review_create", args=(self.product.pk,)),
            {
                "author_name": "آزمایشی",
                "title": "عالی بود",
                "body": "کیفیت برنج خیلی خوب بود و پخت یکدست داشت.",
                "stars": 5,
            },
        )
        self.assertRedirects(response, reverse("product_detail", args=(self.product.pk,)))
        self.assertTrue(ProductReview.objects.filter(product=self.product, title="عالی بود").exists())
        page = self.client.get(reverse("product_detail", args=(self.product.pk,)))
        self.assertContains(page, "عالی بود")
        self.assertContains(page, "pd-reviews")

    def test_empty_product_hides_fake_rating(self):
        page = self.client.get(reverse("product_detail", args=(self.product.pk,)))
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, 'id="pd-rating"')
        self.assertContains(page, "هنوز نظری ثبت نشده")

    def test_staff_can_reply_review(self):
        from catalog.models import ProductReview

        review = ProductReview.objects.create(
            product=self.product,
            author_name="مشتری",
            title="سوال بسته‌بندی",
            body="آیا بسته‌بندی ضد رطوبت است؟",
            stars=4,
        )
        self.client.login(username="09129876543", password="staffpass1")
        inbox = self.client.get(reverse("staff_user_handling"))
        self.assertEqual(inbox.status_code, 200)
        self.assertContains(inbox, "سوال بسته‌بندی")
        reply = self.client.post(
            reverse("staff_review_reply", args=(review.pk,)),
            {"reply_body": "بله، بسته‌بندی کاملاً بهداشتی است.", "reply_name": "برنج رودی"},
        )
        self.assertEqual(reply.status_code, 302)
        review.refresh_from_db()
        self.assertTrue(review.has_reply)
        store = self.client.get(reverse("product_detail", args=(self.product.pk,)))
        self.assertContains(store, "بسته‌بندی کاملاً بهداشتی")
        self.assertContains(store, 'id="pd-rating"')

    def test_soft_catalog_and_review_json(self):
        catalog = self.client.get(
            reverse("product_list"),
            {"q": "هاشمی"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(catalog.status_code, 200)
        data = catalog.json()
        self.assertTrue(data["ok"])
        self.assertGreaterEqual(data["count"], 1)

        review = self.client.post(
            reverse("product_review_create", args=(self.product.pk,)),
            {
                "author_name": "نرم",
                "title": "بدون رفرش",
                "body": "این نظر باید با JSON برگردد.",
                "stars": 4,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(review.status_code, 200)
        payload = review.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["review"]["title"], "بدون رفرش")

        self.client.login(username="09121234567", password="secret12")
        cart = self.client.post(
            reverse("cart_add", args=(self.product.pk,)),
            {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(cart.status_code, 200)
        self.assertTrue(cart.json()["ok"])
        self.assertGreaterEqual(cart.json()["cart_count"], 1)

    def test_inactive_product_not_addable(self):
        self.product.is_active = False
        self.product.save()
        self.client.login(username="09121234567", password="secret12")
        response = self.client.post(reverse("cart_add", args=(self.product.pk,)))
        self.assertEqual(response.status_code, 404)

    def test_signup_rejects_invalid_phone(self):
        response = self.client.post(
            reverse("signup"),
            {
                "full_name": "تست",
                "phone": "123",
                "city": "رشت",
                "postal_code": "",
                "address": "آدرس",
                "password": "secret12",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="123").exists())
