# # from django.urls import path
# # from .views import MyUserViewSet

# # urlpatterns = [
# #     path(
# #         'api/users/', MyUserViewSet.as_view(
# #             {'post': 'create'}
# #         ), name='user-create'),

# #     path(
# #         'api/users/subscriptions/', MyUserViewSet.as_view(
# #             {'get': 'subscriptions'}
# #         ), name='user-subscriptions'),
# # ]
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import MyUserViewSet
# from djoser.views import TokenCreateView

# router = DefaultRouter()

# router.register(r'api/users', MyUserViewSet, basename='user')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('api/', include('djoser.urls')),
#     path('api/', include('djoser.urls.jwt')),
#     path(
#         'api/auth/token/login/', TokenCreateView.as_view(), name='token-login'
#     ),
# ]
