from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited', label='Is Favorited'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart', label='Is in shopping cart'
    )

    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug", label='Tags'
    )

    author = filters.NumberFilter(
        field_name="user__id", label='Author ID'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).prefetch_related(
            'ingredients', 'tags'
        )

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(userfavoriterecipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart_users=self.request.user)
        return queryset
