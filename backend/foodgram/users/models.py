from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    username = models.CharField(
        verbose_name="Логин",
        max_length=100,
        unique=True
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=200,
        unique=True,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=100
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "password",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = 'Пользователи'


    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="subscriber",
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Подписавшийся",
        related_name="subscribing",
    )

    class Meta:
        verbose_name = "Подписка"
        constraints = [
            UniqueConstraint(
                fields=["author", "user"],
                name="unique_subscribing")
        ]

    def __str__(self):
        return f"Автор: {self.user.username}, подписчик: {self.subscribing.username}"

    def following_self(self):
        if self.user == self.subscribing:
            raise ValidationError('Нельзя подписаться на самого себя')
