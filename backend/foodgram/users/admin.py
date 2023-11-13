from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from users.models import Subscription, User


@register(User)
class CustomUserAmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("username", "email")


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
    search_fields = ("user__username", "author__username")
    list_filter = ("user", "author")
    empty_value_display = "-пусто-"
