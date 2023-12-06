from djoser.views import UserViewSet
from .serializers import (
    MyUserCreateSerializer,
    MyUserSubscriptionSerializer,
    MyUserProfileSerializer
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class MyUserViewSet(UserViewSet):
    serializer_class = MyUserCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = MyUserProfileSerializer(user)
        return Response(serializer.data)
 
    # @action(detail=True, methods=['post', 'delete'])
    # def subscribe(self, request, pk=None):
    #     target_user = self.get_object()

    #     current_user = request.user

    #     if not request.user.is_authenticated:
    #         return Response({'detail': 'Authentication required'},
    #                         status=status.HTTP_401_UNAUTHORIZED)

    #     if request.method == 'POST':
    #         if current_user not in target_user.subscribers.all():
    #             target_user.subscribers.add(current_user)

    #     elif request.method == 'DELETE':
    #         if current_user in target_user.subscribers.all():
    #             target_user.subscribers.remove(current_user)

    #     serializer = MyUserSubscriptionSerializer(target_user)

    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['get'])
    # def subscriptions(self, request):
    #     user = self.request.user
    #     subscriptions = user.subscriptions.all()
    #     serializer = MyUserCreateSerializer(subscriptions, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
