import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Basket, Favorite, Ingredient, IngredientInRecipe,
                            Recipe, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from users.models import Subscription, User

User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("name", "measurement_unit")


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')
        read_only_fields = ("__all__",)


class ImageFieldSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            image_data = data.split(";base64,")[-1]
            data = ContentFile(base64.b64decode(image_data), name="photo.jpg")

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, object):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Subscription.objects.filter(
                user=user,
                subscripting=object.id).exists()
        )



class SubscribeSerializer(ModelSerializer):

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "email",
            "username",
            "is_subscribed",
            "recipes_count",
            "recipes",
        )
        read_only_fields = ("email", "username")

    def validate(self, data):
        subscribing = self.instance
        user = self.context.get("request").user
        if Subscription.objects.filter(subscribing=subscribing, user=user).exists():
            raise ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == subscribing:
            raise ValidationError(
                detail="Вы не можете подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, object):
        return object.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()(author=obj.user)
        serializer = RecipeCartSerializer(recipes, many=True,
                                           read_only=True)
        return serializer.data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")

    def validate_amount(self, value):
        if int(value) <= 0:
            raise ValidationError(
                'Количество ингредиента не должно быть 0!'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = ImageFieldSerializer()
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("tags",)

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError("Укажите хотя бы один тег.")
        if len(tags) != len(set(tags)):
            raise ValidationError("Теги не должны повторяться.")


    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise ValidationError("Укажите хотя бы один ингредиент.")
        for ingredient in ingredients:
            get_object_or_404(Ingredient, pk=ingredient["id"])
            try:
                int(ingredient["amount"])
            except ValueError:
                raise ValidationError(
                    "Количество ингредиента должно быть записано только в "
                    "виде числа."
                )
            if int(ingredient["amount"]) < 0:
                raise ValidationError("Минимальное количество игредиента - 0.")
            if ingredient in ingredients_list:
                raise ValidationError("Ингредиенты не должны повторяться.")
            ingredients_list.append(ingredient)
        return ingredients_list

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise ValidationError("Минимальное время приготовления - 1 мин.")

    def validate(self, data):
        tags = self.initial_data.get("tags")
        self.validate_tags(tags)
        data["tags"] = tags

        ingredients = self.initial_data.get("ingredients")
        ingredients_list = self.validate_ingredients(ingredients)
        data["ingredients"] = ingredients_list

        cooking_time = self.initial_data.get("cooking_time")
        self.validate_cooking_time(cooking_time)

        return data


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    image = ImageFieldSerializer()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_basket = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_basket",
        )

    def get_is_favorited(self, object):
        user = self.context.get("request").user
        return (
            not user.is_anonymous
            and user.favorite.filter(recipe=object).exists()
        )

    def get_is_in_basket(self, object):
        user = self.context.get("request").user
        return (
            not user.is_anonymous
            and user.shoppingcart.filter(recipe=object).exists()
        )


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "recipe")

    def validate(self, data):
        user = data.get("user")
        recipe = data.get("recipe")
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError({"error": "Этот рецепт уже добавлен"})
        return data



class BasketSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Basket


class RecipeCartSerializer(ModelSerializer):
    image = ImageFieldSerializer()

    class Meta:
        model = Recipe
        fields = ("name", "image", "cooking_time")
