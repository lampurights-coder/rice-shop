from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from accounts import views as account_views
from catalog import views as catalog_views
from orders import views as order_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    # Storefront
    path("", catalog_views.home, name="home"),
    path(
        "products.html",
        RedirectView.as_view(pattern_name="product_list", permanent=False, query_string=True),
    ),
    path("products/", catalog_views.product_list, name="product_list"),
    path("api/products/search/", catalog_views.product_search_api, name="product_search_api"),
    path("products/<int:pk>/", catalog_views.product_detail, name="product_detail"),
    path("products/<int:pk>/reviews/", catalog_views.product_review_create, name="product_review_create"),
    # Auth
    path("auth/signup/", account_views.signup_view, name="signup"),
    path("auth/login/", account_views.login_view, name="login"),
    path("auth/go/", account_views.auth_go, name="auth_go"),
    path("auth/logout/", account_views.logout_view, name="logout"),
    # User panel
    path("user/", order_views.user_dashboard, name="user_dashboard"),
    path("user/orders/", order_views.order_list, name="user_orders"),
    path("user/orders/<str:code>/cancel/", order_views.order_cancel, name="order_cancel"),
    path("user/cart/", order_views.cart_view, name="user_cart"),
    path("user/cart/add/<int:pk>/", order_views.cart_add, name="cart_add"),
    path("user/cart/<int:item_id>/", order_views.cart_update, name="cart_update"),
    path("user/checkout/", order_views.checkout_view, name="checkout"),
    path("user/profile/", account_views.profile_view, name="user_profile"),
    # Staff panel
    path("staff/", order_views.staff_dashboard, name="staff_dashboard"),
    path("staff/orders/", order_views.staff_orders, name="staff_orders"),
    path("staff/orders/<str:code>/status/", order_views.staff_order_status, name="staff_order_status"),
    path("staff/products/", catalog_views.staff_products, name="staff_products"),
    path("staff/products/new/", catalog_views.staff_product_create, name="staff_product_create"),
    path("staff/products/<int:pk>/edit/", catalog_views.staff_product_edit, name="staff_product_edit"),
    path("staff/products/<int:pk>/delete/", catalog_views.staff_product_delete, name="staff_product_delete"),
    path("staff/products/<int:pk>/images/add/", catalog_views.staff_product_image_add, name="staff_product_image_add"),
    path(
        "staff/products/<int:pk>/images/<int:image_id>/primary/",
        catalog_views.staff_product_image_primary,
        name="staff_product_image_primary",
    ),
    path(
        "staff/products/<int:pk>/images/<int:image_id>/delete/",
        catalog_views.staff_product_image_delete,
        name="staff_product_image_delete",
    ),
    path("staff/customers/", order_views.staff_customers, name="staff_customers"),
    path("staff/analytics/", order_views.staff_analytics, name="staff_analytics"),
    path("staff/user-handling/", catalog_views.staff_user_handling, name="staff_user_handling"),
    path("staff/reviews/<int:review_id>/reply/", catalog_views.staff_review_reply, name="staff_review_reply"),
    path("staff/reviews/<int:review_id>/toggle/", catalog_views.staff_review_toggle, name="staff_review_toggle"),
    path("staff/site/", catalog_views.staff_site_settings, name="staff_site_settings"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
