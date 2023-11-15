from django.contrib.auth import get_user_model
from django_filters import FilterSet, filters
from recipes.models import Ingredient, Recipe

User = get_user_model()

class IngredientFilter(FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(FilterSet):
    author = filters.AllValuesMultipleFilter(field_name="author__id")

    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug",
    )

    is_favorited = filters.NumberFilter(method="filter_is_favorited")

    is_in_basket = filters.NumberFilter(method="filter_is_in_basket")

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_basket")

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_basket(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(basket__user=self.request.user)
        return queryset
