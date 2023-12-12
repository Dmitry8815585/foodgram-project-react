from users.models import MyUser, UserSubscription
from .serializers import (
    MyUserCreateSerializer,
    MyUserProfileSerializer,
    MyUserSubscriptionSerializer
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets


class MyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 1000


class MyUserViewSet(viewsets.ModelViewSet):

    queryset = MyUser.objects.all()
    pagination_class = MyPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return MyUserCreateSerializer
        elif self.action in ['profile', 'subscribe', 'subscriptions']:
            return MyUserProfileSerializer
        elif self.action == 'retrieve':
            return MyUserProfileSerializer
        else:
            return MyUserSubscriptionSerializer

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
        else:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
