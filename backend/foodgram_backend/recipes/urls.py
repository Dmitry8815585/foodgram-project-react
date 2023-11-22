from rest_framework.routers import DefaultRouter
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()
router.register(r'api/tags', TagViewSet, basename='tag')
router.register(r'api/ingredients', IngredientViewSet, basename='ingredient')
router.register(r'api/recipes', RecipeViewSet, basename='recipe')

urlpatterns = router.urls
