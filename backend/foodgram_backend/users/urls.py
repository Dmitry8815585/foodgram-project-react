from django.urls import path
from .views import MyUserCreateView

urlpatterns = [
    path('api/users/', MyUserCreateView.as_view(), name='create-user'),
]
