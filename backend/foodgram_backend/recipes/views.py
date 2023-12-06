from rest_framework import viewsets
from .models import (
    Recipe, RecipeIngredient, ShoppingCartItem, Tag,
    Ingredient, UserFavoriteRecipe
)
from .serializers import (
    RecipeSerializer, RecipeIngredientSerializer,
    TagSerializer, IngredientSerializer
)

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from django.http import HttpResponse
from collections import defaultdict
from .permissions import IsRecipeAuthor


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthor]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = self.get_object()

        user_favorite, created = UserFavoriteRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )

        if request.method == 'POST' and not created:
            return Response(
                {'detail': 'Recipe already in favorites.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE' and not created:
            user_favorite.delete()

        response_data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': request.build_absolute_uri(recipe.image.url) if (
                recipe.image
            ) else None,
            'cooking_time': recipe.cooking_time,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
        )
    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            ShoppingCartItem.objects.get_or_create(user=user, recipe=recipe)
        elif request.method == 'DELETE':
            ShoppingCartItem.objects.filter(user=user, recipe=recipe).delete()

        response_data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': request.build_absolute_uri(recipe.image.url) if (
                recipe.image
            ) else None,
            'cooking_time': recipe.cooking_time,
            'is_in_shopping_cart': recipe.is_in_user_shopping_cart(user),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        recipes_in_cart = Recipe.objects.filter(
            shopping_cart_users=request.user
        )

        shopping_cart_dict = defaultdict(int)

        for recipe in recipes_in_cart:
            for ingredient in recipe.recipe_ingredients.all():
                key = f"{ingredient.ingredient.name}"
                shopping_cart_dict[key] += ingredient.amount

        shopping_cart_text = "\n".join(
            f"{key} ----- {amount}"
            f" ({ingredient.ingredient.measurement_unit})" for (
                key, amount
            ) in shopping_cart_dict.items()
        )

        response = HttpResponse(shopping_cart_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
