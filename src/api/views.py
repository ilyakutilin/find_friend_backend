from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from events.models import Event
from users.models import Interest, User

from .filters import EventSearchFilter, EventsFilter, UserFilter
from .pagination import EventPagination, MyPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import EventSerializer  # MyUserGetSerializer,
from .serializers import (
    FriendSerializer,
    InterestSerializer,
    MyUserCreateSerializer,
    MyUserSerializer,
)
from .services import FriendRequestService


class MyUserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = MyPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = UserFilter
    search_fields = ["email", "first_name", "last_name"]
    permission_classes = [
        IsAdminOrAuthorOrReadOnly,
    ]

    def get_serializer_class(self):
        """Выбор сериализатора."""
        # if self.request.method == "GET":
        #    return MyUserGetSerializer
        if self.request.method == "POST":
            return MyUserCreateSerializer
        return MyUserSerializer

    @swagger_auto_schema(
        responses={
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "first_name": ["Обязательное поле."],
                        "last_name": ["Обязательное поле."],
                        "age": ["Обязательное поле."],
                        "interests": ["Обязательное поле."],
                        "friends_count": ["Обязательное поле."],
                    }
                },
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        """Создание пользователя."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                },
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """Получение списка пользователей."""
        return super().list(request, *args, **kwargs)

    # "Выключение" неиспользуемых эндпоинтов джозера
    @swagger_auto_schema(auto_schema=None)
    def activation(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def resend_activation(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def reset_password(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def reset_password_confirm(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def set_username(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def reset_username(self, request, *args, **kwargs):  # noqa
        pass

    @swagger_auto_schema(auto_schema=None)
    def reset_username_confirm(self, request, *args, **kwargs):  # noqa
        pass


class FriendRequestViewSet(ModelViewSet):
    """Вьюсет добавления в друзья."""

    serializer_class = FriendSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """Получение queryset'а."""
        return FriendRequestService.get_user_friend_requests(self.request.user)

    def perform_create(self, serializer):
        """Создание запроса в друзья."""
        friend_id = self.request.data.get("friend")
        if friend_id is not None:
            serializer.save(initiator=self.request.user, friend_id=friend_id)
        else:
            raise ValueError("ID друга не был передан")

    # def perform_create(self, serializer):
    #     FriendRequestService.create_friend_request(serializer,
    #                                                self.request.user)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_request(self, request, pk=None):
        """Принятие запроса в друзья."""
        message = FriendRequestService.respond_to_friend_request(
            pk, request.user, True
        )
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="decline")
    def decline_request(self, request, pk=None):
        """Отклонение запроса в друзья."""
        message = FriendRequestService.respond_to_friend_request(
            pk, request.user, False
        )
        return Response({"message": message}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            401: openapi.Response(
                description="UnauthorizedAccess",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                },
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """Получение списка друзей."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                },
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        """Добавление в друзья."""
        return super().create(request, *args, **kwargs)


class EventViewSet(ModelViewSet):
    """Вьюсет мероприятия пользователя."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (EventSearchFilter, DjangoFilterBackend)
    filterset_class = EventsFilter
    pagination_class = EventPagination
    permission_classes = [
        IsAdminOrAuthorOrReadOnly,
    ]

    @swagger_auto_schema(
        responses={
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                },
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """Получение списка мероприятий."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            401: openapi.Response(
                description="Unauthorized",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                },
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        """Создание мероприятия."""
        return super().create(request, *args, **kwargs)


class InterestViewSet(ReadOnlyModelViewSet):
    """Отображение интересов."""

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    pagination_class = None
