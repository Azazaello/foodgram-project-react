from django.contrib import admin
from users.models import Subscription, User


@admin.register(User)
class UserAmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "password"
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "subscribing",
    )
    search_fields = ("username", "subscribing")
