from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientFilter, RecipeFilter
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCartItem,
    Tag,
    UserFavoriteRecipe
)
from .permissions import IsRecipeAuthor
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().select_related('user')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save(user=request.user)
        except serializers.ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart_data = Recipe.objects.filter(
            shopping_cart_users=request.user
        ).values(
            ingredient_name=F('recipe_ingredients__ingredient__name'),
            measurement_unit=F(
                'recipe_ingredients__ingredient__measurement_unit'
            ),
        ).annotate(
            total_quantity=Sum('recipe_ingredients__amount')
        )

        shopping_cart_text = "\n".join(
            f"{data['ingredient_name']} ---"
            + f" {data['total_quantity']} ({data['measurement_unit']})"
            for data in shopping_cart_data
        )

        response = HttpResponse(
            shopping_cart_text, content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


class FavoriteRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user_favorite, created = UserFavoriteRecipe.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            return Response(
                {'detail': 'Recipe already in favorites.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = FavoriteSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        try:
            user_favorite = UserFavoriteRecipe.objects.get(
                user=request.user,
                recipe=recipe
            )
            user_favorite.delete()
        except UserFavoriteRecipe.DoesNotExist:
            return Response(
                {'detail': 'Recipe not in favorites.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        ShoppingCartItem.objects.get_or_create(user=user, recipe=recipe)

        serializer = ShoppingCartSerializer(
            recipe, context={'request': request}
        )
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        ShoppingCartItem.objects.filter(user=user, recipe=recipe).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
