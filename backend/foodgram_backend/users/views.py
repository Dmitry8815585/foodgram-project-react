from django.shortcuts import get_object_or_404

from recipes.pagination import MyPagination
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import MyUser, UserSubscription

from .serializers import (
    MyUserCreateSerializer,
    MyUserProfileSerializer,
    MyUserSubscriptionSerializer,
    SubscribeUserSerializer
)


class MyUserViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.AllowAny]
    queryset = MyUser.objects.all()
    pagination_class = MyPagination
    serializer_class = MyUserCreateSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return MyUserCreateSerializer
        if self.action in [
            'profile',
            'subscribe',
            'subscriptions',
            'retrieve'
        ]:
            return MyUserProfileSerializer
        return MyUserSubscriptionSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')

        if user_id:
            user = get_object_or_404(MyUser, pk=user_id)
            return MyUser.objects.filter(pk=user.id)

        return MyUser.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MyUserProfileSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = MyUserProfileSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=['get'], url_path='me')
    def current_user(self, request):
        user = self.request.user

        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = MyUserProfileSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = MyUserProfileSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = user.subscriptions.all()
        page = self.paginate_queryset(subscriptions)

        if page is not None:
            serializer = MyUserSubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = MyUserSubscriptionSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        if request.user.is_authenticated:
            user = request.user
            new_password = request.data.get('new_password')

            if not user.check_password(request.data.get('current_password')):
                return Response(
                    {'detail': 'Incorrect current password'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class SubscribeUserView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        target_user = get_object_or_404(MyUser, pk=pk)
        current_user = request.user

        serializer = SubscribeUserSerializer(
            target_user, data=request.data, context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        UserSubscription.objects.create(
            from_user=current_user, to_user=target_user
        )

        serializer = MyUserSubscriptionSerializer(
            target_user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        target_user = get_object_or_404(MyUser, pk=pk)
        current_user = request.user

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

        return Response(status=status.HTTP_204_NO_CONTENT)
