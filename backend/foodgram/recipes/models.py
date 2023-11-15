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
        verbose_name="Цвет",
        max_length=7,
        unique=True,
    )

    slug = models.SlugField(
        verbose_name="Тег (slug)",
        max_length=20,
        unique=True,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
        related_name="recipe_author",
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
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="IngredientInRecipe",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name="recipes"
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
        ordering = ["-id"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name[:50]}"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_list",
        verbose_name="Рецепт",
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
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return (
            f"{self.recipe}: {self.ingredient.name},"
            f" {self.amount}, {self.ingredient.measurement_unit}"
        )


class Basket(models.Model):

    class Meta:
        verbose_name = "Корзина"
        unique_together = ('user', 'recipe')


class Favorite(models.Model):

    class Meta:
        verbose_name = "Избранное"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique favorite"
            ),
        ]

    def __str__(self):
        return f"{self.user.username}, {self.recipe.name}."
