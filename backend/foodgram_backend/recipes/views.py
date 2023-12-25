from collections import defaultdict

from django.db.models import Q
from django.http import Http404, HttpResponse

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
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

        name_query = self.request.query_params.get('name', None)

        if name_query:
            return Ingredient.objects.filter(name__icontains=name_query)

        return Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthor]

    def get_object(self):
        try:
            return Recipe.objects.get(pk=self.kwargs['pk'])
        except Recipe.DoesNotExist:
            raise Http404

    def get_queryset(self):

        is_favorited_param = self.request.query_params.get(
            'is_favorited', None
        )

        if is_favorited_param == '1':
            if not self.request.user.is_authenticated:
                raise PermissionDenied(
                    detail='Учетные данные не были предоставлены.'
                )

            return Recipe.objects.filter(
                userfavoriterecipe__user=self.request.user
            )

        author_id = self.request.query_params.get('author', None)

        if author_id:
            return Recipe.objects.filter(user__id=author_id)

        tag_slugs = self.request.query_params.getlist('tags', None)

        if tag_slugs:
            tag_queries = [Q(tags__slug=tag_slug) for tag_slug in tag_slugs]

            tag_filter = tag_queries.pop()

            for tag_query in tag_queries:
                tag_filter |= tag_query

            return Recipe.objects.filter(tag_filter).distinct()

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None
        )

        if is_in_shopping_cart == '1':
            if self.request.user.is_authenticated:
                return Recipe.objects.filter(
                    shopping_cart_users=self.request.user
                )
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Recipe.objects.all()

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
        if request.method == 'DELETE' and not created:
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
            f"{key} --- {quantity} ({ingredient.ingredient.measurement_unit})"
            for key, quantity in shopping_cart_dict.items()
        )

        response = HttpResponse(shopping_cart_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
