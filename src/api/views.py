from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from config.constants import MAX_DISTANCE
from events.models import Event, EventLocation, ParticipationRequest
from notifications.models import Notification, NotificationSettings
from users.models import (
    Blacklist,
    City,
    FriendRequest,
    Friendship,
    Interest,
    User,
    UserLocation,
)

from .filters import EventsFilter, UserFilter
from .geo import (
    get_event_distance,
    get_event_location,
    get_user_distance,
    get_user_location,
    save_user_location,
)
from .pagination import EventPagination, MyPagination
from .permissions import (
    IsAdminOrAuthorOrReadOnly,
    IsAdminOrAuthorOrReadOnlyAndNotBlocked,
    IsEventOrganizer,
    IsRecipient,
)
from .serializers import (
    BlacklistSerializer,
    CitySerializer,
    EventSerializer,
    FriendRequestSerializer,
    InterestSerializer,
    MyEventSerializer,
    MyUserCreateSerializer,
    MyUserSerializer,
    NotificationSerializer,
    NotificationSettingsSerializer,
    ParticipationSerializer,
)
from .services import FriendRequestService, ParticipationRequestService


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
        IsAdminOrAuthorOrReadOnlyAndNotBlocked,
    ]

    def get_serializer_class(self):
        """Выбор сериализатора."""
        # Сохранение геолокации текущего пользователя
        save_user_location(self.request.user)
        if self.request.method == "POST":
            return MyUserCreateSerializer
        return MyUserSerializer

    def list(self, request, *args, **kwargs):
        """Получение списка пользователей."""
        if not request.user.is_staff:
            blocks = Blacklist.objects.filter(blocked_user=request.user)
            if blocks.exists():
                blockers = []
                for obj in blocks:
                    blockers.append(obj.user.id)
                queryset = User.objects.all().exclude(id__in=blockers)
                serializer = MyUserSerializer(
                    queryset, many=True, context={"request": request}
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["get"],
        url_path="my_friends",
        permission_classes=(IsAuthenticated,),
    )
    def my_friends(self, request):
        """Вывод друзей текущего пользователя."""
        friendships = Friendship.objects.filter(
            initiator=self.request.user
        ) | Friendship.objects.filter(friend=self.request.user)
        friends = []
        for friendship in friendships:
            if friendship.initiator == self.request.user:
                friends.append(friendship.friend)
            else:
                friends.append(friendship.initiator)
        serializer = MyUserSerializer(
            friends, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="my_events",
        permission_classes=(IsAuthenticated,),
    )
    def my_events(self, request):
        """Вывод мероприятий текущего пользователя."""
        queryset = Event.objects.filter(event__user=self.request.user)
        serializer = MyEventSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def block(self, request, **kwargs):
        """Добавление/удаление пользователя в черный список."""
        user = request.user
        blocked_user_id = self.kwargs.get("id")
        blocked_user = get_object_or_404(User, id=blocked_user_id)
        if request.method == "POST":
            serializer = BlacklistSerializer(
                blocked_user, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Blacklist.objects.create(user=user, blocked_user=blocked_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        block = get_object_or_404(
            Blacklist, user=user, blocked_user=blocked_user
        )
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def blacklist(self, request):
        """Получение черного списка."""
        user = request.user
        queryset = User.objects.filter(blocked__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = BlacklistSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def geolocation(self, request, **kwargs):
        """Получение геолокации пользователя."""
        user_id = self.kwargs.get("id")
        user = get_object_or_404(User, id=user_id)
        data = get_user_location(user)
        if data:
            return Response(data, status=status.HTTP_200_OK)
        message = f"Геолокация пользователя {user} не найдена."
        return HttpResponse(message, status=404)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def distance(self, request, **kwargs):
        """Получение расстояния до пользователя от текущего пользователя."""
        user_id = self.kwargs.get("id")
        user = get_object_or_404(User, id=user_id)
        data = get_user_distance(request.user, user)
        if data is not None:
            return Response(data, status=status.HTTP_200_OK)
        message = f"Расстояние до пользователя {user} не найдено."
        return HttpResponse(message, status=404)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def distances(self, request):
        """Получение расстояния до пользователей от текущего пользователя."""
        locations = UserLocation.objects.all().exclude(user=self.request.user)
        data = []
        if self.request.query_params and self.request.query_params["search"]:
            max_distance = int(self.request.query_params["search"])
        else:
            max_distance = MAX_DISTANCE
        for location in locations:
            distance = get_user_distance(
                self.request.user, location.user, (location.lat, location.lon)
            )
            if distance and distance["distance"] <= max_distance:
                data.append(
                    {
                        "user": location.user.id,
                        "first_name": location.user.first_name,
                        "last_name": location.user.last_name,
                        "distance": distance["distance"],
                    }
                )
        return Response(data, status=status.HTTP_200_OK)


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

    # TODO: drf-yasg: Update decorator
    # @swagger_auto_schema(
    #     responses={
    #         401: openapi.Response(
    #             description="UnauthorizedAccess",
    #             examples={
    #                 "application/json": {
    #                     "detail": "Учетные данные не были предоставлены."
    #                 }
    #             },
    #         ),
    #     },
    # )
    def list(self, request, *args, **kwargs):
        """Получение списка друзей."""
        return super().list(request, *args, **kwargs)

    # TODO: drf-yasg: Update decorator
    # @swagger_auto_schema(
    #     responses={
    #         401: openapi.Response(
    #             description="Unauthorized",
    #             examples={
    #                 "application/json": {
    #                     "detail": "Учетные данные не были предоставлены."
    #                 }
    #             },
    #         ),
    #     },
    # )
    def create(self, request, *args, **kwargs):
        """Добавление в друзья."""
        return super().create(request, *args, **kwargs)


class EventViewSet(ModelViewSet):
    """Отображение мероприятий."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = EventsFilter
    search_fields = [
        "name",
        "event_type",
        "city__name",
        "address",
    ]
    pagination_class = EventPagination
    permission_classes = [
        IsAdminOrAuthorOrReadOnly,
    ]

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def geolocation(self, request, **kwargs):
        """Получение геолокации мероприятия."""
        event_id = self.kwargs.get("pk")
        event = get_object_or_404(Event, id=event_id)
        data = get_event_location(event)
        if data:
            return Response(data, status=status.HTTP_200_OK)
        message = f"Геолокация мероприятия {event} не найдена."
        return HttpResponse(message, status=404)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def distance(self, request, **kwargs):
        """Получение расстояния до мероприятия от текущего пользователя."""
        event_id = self.kwargs.get("pk")
        event = get_object_or_404(Event, id=event_id)
        data = get_event_distance(request.user, event)
        if data is not None:
            return Response(data, status=status.HTTP_200_OK)
        message = f"Расстояние до мероприятия {event} не найдено."
        return HttpResponse(message, status=404)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def distances(self, request):
        """Получение расстояния до мероприятий от текущего пользователя."""
        locations = EventLocation.objects.all()
        data = []
        if self.request.query_params and self.request.query_params["search"]:
            max_distance = int(self.request.query_params["search"])
        else:
            max_distance = MAX_DISTANCE
        for location in locations:
            distance = get_event_distance(
                self.request.user, location.event, (location.lat, location.lon)
            )
            if distance and distance["distance"] <= max_distance:
                data.append(
                    {
                        "event": location.event.id,
                        "name": location.event.name,
                        "distance": distance["distance"],
                    }
                )
        return Response(data, status=status.HTTP_200_OK)


class ParticipationViewSet(ModelViewSet):
    """ViewSet для управления заявками на участие в мероприятии."""

    serializer_class = ParticipationSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        """Возвращает queryset заявок на участие в мероприятии."""
        return ParticipationRequest.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        """Переопределяет метод создания объекта.

        автоматически назначая отправителя заявки текущим пользователем.
        """
        serializer.save(from_user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        url_path="accept",
        permission_classes=[
            IsEventOrganizer,
        ],
    )
    def accept_request(self, request, pk=None):
        """Обрабатывает принятие заявки на мероприятие."""
        ParticipationRequestService.accept_event_participation(
            pk, request.user
        )
        return Response(
            {"message": "Заявка на участие в мероприятии принята."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="decline",
        permission_classes=[IsEventOrganizer],
    )
    def decline_request(self, request, pk=None):
        """Обрабатывает отклонение заявки на мероприятие."""
        ParticipationRequestService.decline_event_participation(
            pk, request.user
        )
        return Response(
            {"message": "Заявка на участие в мероприятии отклонена."},
            status=status.HTTP_200_OK,
        )


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


class NotificationViewSet(ModelViewSet):
    """Вьюсет уведомлений пользователя."""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Получает список уведомлений текущего пользователя."""
        user = self.request.user
        return (
            Notification.objects.filter(recipient=user)
            .select_related("recipient")
            .order_by("-created_at")
        )

    @action(detail=False, methods=["patch"], url_path="notification_settings")
    def update_notification_settings(self, request):
        """Обновляет настройки уведомлений текущего пользователя."""
        user = request.user
        try:
            settings = NotificationSettings.objects.get(user=user)
            serializer = NotificationSettingsSerializer(
                instance=settings, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except NotificationSettings.DoesNotExist:
            return Response(
                {"error": "Настройки уведомлений не найдены."},
                status=status.HTTP_404_NOT_FOUND,
            )
