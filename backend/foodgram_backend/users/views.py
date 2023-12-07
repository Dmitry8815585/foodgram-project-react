from djoser.views import UserViewSet

from users.models import UserSubscription
from .serializers import (
    MyUserCreateSerializer,
    MyUserProfileSerializer,
    MyUserSubscriptionSerializer
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly
)


class MyUserViewSet(UserViewSet):
    serializer_class = MyUserCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path='me')
    def current_user(self, request):
        user = self.request.user
        serializer = MyUserProfileSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = MyUserProfileSerializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        target_user = self.get_object()
        serializer = MyUserSubscriptionSerializer(
            target_user, context={'request': request}
        )

        current_user = request.user

        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if current_user == target_user:
            return Response(
                {'detail': 'Cannot subscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if UserSubscription.objects.filter(
                from_user=current_user, to_user=target_user
            ).exists():
                return Response(
                    {'detail': 'Already subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            UserSubscription.objects.create(
                from_user=current_user, to_user=target_user
            )

        elif request.method == 'DELETE':
            try:
                subscription = UserSubscription.objects.get(
                    from_user=current_user, to_user=target_user
                )
                subscription.delete()
            except UserSubscription.DoesNotExist:
                return Response(
                    {'detail': 'Not subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = user.subscriptions.all()
        serializer = MyUserSubscriptionSerializer(
            subscriptions, many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
