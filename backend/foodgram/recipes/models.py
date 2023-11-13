from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=100
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=100
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Тег",
        max_length=20,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цветовой HEX-код",
        max_length=7,
        unique=True,
    )

    slug = models.SlugField(
        verbose_name="Тег (slug)",
        max_length=10,
        unique=True,
    )

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        related_name="recipe_author",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта"
    )
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        upload_to="recipe/",
        blank=True,
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="IngredientInRecipe",
        through_fields=("recipe", "ingredient")
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipe"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                limit_value=1,
                message=(
                    "Время приготовления не может быть менее 0 минуты."
                ),
            ),
            MaxValueValidator(
                limit_value=2880,
                message=("Время приготовления не может быть более 2-х суток."),
            ),
        ],
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name[:50]}"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="ingredient_in",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(
            MinValueValidator(
                limit_value=1, message="Количество не должно быть меньше нуля"
            ),
        ),
    )

    class Meta:
        verbose_name = "Количество в рецепте"
        constraints = [
            UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique ingredient for recipe",
            )
        ]

    def __str__(self):
        return (
            f"{self.recipe}: {self.ingredient.name},"
            f" {self.amount}, {self.ingredient.measurement_unit}"
        )


class Cart(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="cart_recipe",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь списка покупок",
        related_name="cart_user",
        on_delete=models.CASCADE,
    )
    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique cart"
            ),
        ]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="favorite_recipe",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь списка покупок",
        related_name="favorite_user",
        on_delete=models.CASCADE,
    )
    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique favorite"
            ),
        ]

    def __str__(self):
        return f"{self.user.username}, {self.recipe.name}."
