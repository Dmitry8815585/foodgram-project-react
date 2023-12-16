from collections import defaultdict
from django.shortcuts import get_object_or_404

from django.http import HttpResponse

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

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
    IngredientSerializer,
    RecipeIngredientSerializer,
    RecipeSerializer,
    TagSerializer
)


class MyPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 1000


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

    def get_queryset(self):
        queryset = Ingredient.objects.all()

        name_query = self.request.query_params.get('name', None)

        if name_query:
            queryset = queryset.filter(name__icontains=name_query)

        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthor]

    # def create(self, serializer):
    #     ingredients_data = self.request.data.get('ingredients', [])
    #     tags_data = self.request.data.get('tags', [])

    #     for ingredient_data in ingredients_data:
    #         ingredient_id = ingredient_data.get('ingredient')
    #         if not Ingredient.objects.filter(pk=ingredient_id).exists():
    #             return Response(
    #                 {'detail': (
    #                     f'Ingredient with id {ingredient_id} does not exist.'
    #                 )},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         amount = ingredient_data.get('amount')

    #         if amount is not None and amount < 1:
    #             return Response(
    #                 {'detail': (
    #                     'Ingredient amount must be greater than or equal to 1.'
    #                 )},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #     if len(ingredients_data) != len(
    #         set((item['ingredient'] for item in ingredients_data))
    #     ):
    #         return Response(
    #             {'detail': 'Duplicate ingredients are not allowed.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     if len(tags_data) != len(set(tags_data)):
    #         return Response(
    #             {'detail': 'Duplicate tags are not allowed.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     for tag_id in tags_data:
    #         if not Tag.objects.filter(pk=tag_id).exists():
    #             return Response(
    #                 {'detail': f'Tag with id {tag_id} does not exist.'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #     if not self.request.data.get('image'):
    #         return Response(
    #             {'detail': 'Image field is required.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     cooking_time = self.request.data.get('cooking_time')
    #     if cooking_time is not None and cooking_time < 1:
    #         return Response(
    #             {'detail': 'Cooking time must be greater than or equal to 1.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     serializer.save(user=self.request.user)
    def get_queryset(self):
        queryset = Recipe.objects.all()

        tag_slug = self.request.query_params.get('tags', None)

        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=tag)

        is_favorited_param = self.request.query_params.get(
            'is_favorited', None
        )

        if is_favorited_param == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    userfavoriterecipe__user=self.request.user
                )
            else:
                return Response(
                    {'detail': 'Учетные данные не были предоставлены.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None
        )

        if is_in_shopping_cart == '1':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    shopping_cart_users=self.request.user
                )
            else:
                return Response(
                    {'detail': 'Учетные данные не были предоставлены.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
        )
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
