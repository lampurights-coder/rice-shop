from django.contrib import admin

from accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "city", "user")
    search_fields = ("full_name", "phone", "city")
