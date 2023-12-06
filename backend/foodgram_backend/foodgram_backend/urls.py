from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from recipes.views import (
    RecipeViewSet, TagViewSet, IngredientViewSet, RecipeIngredientViewSet
)
from users.views import MyUserViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(
    r'recipesingredients', RecipeIngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users', MyUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
