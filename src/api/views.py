from django.db.models import Q
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
from users.models import City, FriendRequest, Interest, User

from .filters import EventsFilter, UserFilter
from .pagination import EventPagination, MyPagination
from .permissions import IsAdminOrAuthorOrReadOnly, IsRecipient
from .serializers import CitySerializer  # MyUserGetSerializer,
from .serializers import (
    EventSerializer,
    FriendRequestSerializer,
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
    search_fields = [
        "email",
        "first_name",
        "last_name",
        "birthday",
        "city__name",
    ]
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

    @action(
        detail=False,
        methods=["get"],
        url_path="myfriends",
        permission_classes=(IsAuthenticated,),
    )
    def my_friends(self, request):
        """Вывод друзей текущего пользователя."""
        queryset = User.objects.filter(sent_requests__is_added=True).exclude(
            id=self.request.user.id
        )
        serializer = MyUserSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendRequestViewSet(ModelViewSet):
    """ViewSet для управления заявками на дружбу.

    Поддерживает создание, просмотр, принятие и отклонение заявок.
    """

    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает queryset заявок на дружбу.

        связанных с текущим пользователем, как отправителем, так и получателем.
        """
        return FriendRequest.objects.select_related(
            "from_user", "to_user"
        ).filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))

    def perform_create(self, serializer):
        """Переопределяет метод создания объекта.

        автоматически назначая отправителя заявки текущим пользователем.
        """
        serializer.save(from_user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        url_path="accept",
        permission_classes=[IsAuthenticated, IsRecipient],
    )
    def accept_request(self, request, pk=None):
        """Обрабатывает принятие заявки на дружбу текущим пользователем."""
        FriendRequestService.accept_friend_request(pk, request.user)
        return Response(
            {"message": "Заявка на дружбу принята."}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="decline",
        permission_classes=[IsAuthenticated, IsRecipient],
    )
    def decline_request(self, request, pk=None):
        """Обрабатывает отклонение заявки на дружбу текущим пользователем."""
        FriendRequestService.decline_friend_request(pk, request.user)
        return Response(
            {"message": "Заявка на дружбу отклонена."},
            status=status.HTTP_200_OK,
        )

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
    filter_backends = (
        # EventSearchFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = EventsFilter
    search_fields = [
        "name",
        "event_type",
        "date",
        "city__name",
    ]
    pagination_class = EventPagination
    permission_classes = [
        IsAdminOrAuthorOrReadOnly,
    ]

    @action(
        detail=False,
        methods=["get"],
        url_path="myevents",
        permission_classes=(IsAuthenticated,),
    )
    def my_events(self, request):
        """Вывод мероприятий текущего пользователя."""
        events = Event.objects.filter(
            event__is_organizer=True, event__user=self.request.user
        )
        serializer = EventSerializer(
            events, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class CityViewSet(ReadOnlyModelViewSet):
    """Отображение городов."""

    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = [
        "name",
    ]
    pagination_class = None
