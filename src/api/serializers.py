from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SlugRelatedField

from events.models import Event, EventMember
from users.models import City, Friend, Interest, User, UserInterest
from users.validators import (
    EMAIL_LENGTH_MSG,
    FIRST_NAME_LENGTH_MSG,
    INVALID_EMAIL_MSG,
    LAST_NAME_LENGTH_MSG,
)


class InterestSerializer(ModelSerializer):
    """Сериализатор интересов."""

    class Meta:
        model = Interest
        fields = ("id", "name")


class MyUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    city = SlugRelatedField(
        slug_field="name",
        queryset=City.objects.all(),
        required=False,
        allow_null=True,
    )
    interests = InterestSerializer(many=True)
    age = serializers.IntegerField()
    friends_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "birthday",
            "sex",
            "age",
            "interests",
            "friends",
            "friends_count",
            "city",
            "interests",
            "avatar",
            "profession",
            "purpose",
            "network_nick",
            "additionally",
        )

    def create(self, validated_data):
        """Создание пользователя с указанными интересами и друзьями."""
        if "interests" not in self.initial_data:
            return User.objects.create(**validated_data)
        interests = validated_data.pop("interests")
        if "friends" not in self.initial_data:
            return User.objects.create(**validated_data)
        friends = validated_data.pop("friends")
        user = User.objects.create(**validated_data)
        for interest in interests:
            current_interest = Interest.objects.get(**interest)
            UserInterest.objects.create(user=user, interest=current_interest)
        for friend in friends:
            current_friend = User.objects.get(**friend)
            Friend.objects.create(
                initiator=user, friend=current_friend, is_added=friend.is_added
            )
        return user

    def update(self, instance, validated_data):
        """Обновление пользователя с указанными интересами и друзьями."""
        if "interests" not in self.initial_data:
            return super().update(instance, validated_data)
        interests = validated_data.pop("interests")
        for interest in interests:
            current_interest = Interest.objects.get(**interest)
            UserInterest.objects.create(
                user=instance, interest=current_interest
            )
        if "friends" not in self.initial_data:
            return super().update(instance, validated_data)
        friends = validated_data.pop("friends")
        for friend in friends:
            current_friend = User.objects.get(**friend)
            Friend.objects.create(
                initiator=instance,
                friend=current_friend,
                is_added=friend.is_added,
            )
        return super().update(instance, validated_data)


class MyUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            "password",
            "birthday",
        )
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "max_length": EMAIL_LENGTH_MSG,
                    "min_length": EMAIL_LENGTH_MSG,
                    "invalid": INVALID_EMAIL_MSG,
                }
            },
            "first_name": {
                "error_messages": {
                    "max_length": FIRST_NAME_LENGTH_MSG,
                    "min_length": FIRST_NAME_LENGTH_MSG,
                }
            },
            "last_name": {
                "error_messages": {
                    "max_length": LAST_NAME_LENGTH_MSG,
                    "min_length": LAST_NAME_LENGTH_MSG,
                }
            },
        }


class MyUserGetSerializer(UserSerializer):
    """Сериализатор пользователя."""

    city = SlugRelatedField(
        slug_field="name",
        queryset=City.objects.all(),
        required=False,
        allow_null=True,
    )
    age = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "age",
            "city",
        )


class FriendSerializer(ModelSerializer):
    """Сериализатор друга пользователя."""

    class Meta:
        model = Friend
        fields = (
            "id",
            "initiator",
            "friend",
            "is_added",
        )

    def validate(self, data):
        """Валидация друзей."""
        if not data:
            raise ValidationError(
                detail="Ошибка с выбором друга",
                code=status.HTTP_400_BAD_REQUEST,
            )
        initiator = data["initiator"]
        friend = data["friend"]
        if not initiator or not initiator.is_active:
            raise ValidationError(
                detail=f"Нет такого пользователя {initiator}",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if not friend or not friend.is_active:
            raise ValidationError(
                detail=f"Нет такого друга {friend}",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if (
            Friend.objects.filter(initiator=initiator, friend=friend).exists()
            or Friend.objects.filter(
                initiator=friend, friend=initiator
            ).exists()
        ):
            raise ValidationError(
                detail="Повторная дружба невозможна",
                code=status.HTTP_400_BAD_REQUEST,
            )
        if initiator == friend:
            raise ValidationError(
                detail="Дружба с самим собой невозможна",
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class EventSerializer(ModelSerializer):
    """Сериализатор мероприятия пользователя."""

    interests = InterestSerializer(many=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "description",
            "interests",
            "members",
            "event_type",
            "date",
            "city",
            "event_price",
            "image",
        )

    '''
    def create(self, validated_data):
        """Создание мероприятия с указанными интересами."""
        if "interests" not in self.initial_data:
            return Event.objects.create(**validated_data)
        interests = validated_data.pop("interests")
        event = Event.objects.create(**validated_data)
        for interest in interests:
            current_interest = Interest.objects.get(**interest)
            EventInterest.objects.create(
                event=event, interest=current_interest
            )
        return event

    def update(self, instance, validated_data):
        """Обновление мероприятия с указанными интересами."""
        if "interests" not in self.initial_data:
            return super().update(instance, validated_data)
        interests = validated_data.pop("interests")
        for interest in interests:
            current_interest = Interest.objects.get(**interest)
            EventInterest.objects.create(
                event=instance, interest=current_interest
            )
        return super().update(instance, validated_data)
    '''

    def create(self, validated_data):
        """Создание мероприятия с указанными участниками."""
        if "members" not in self.initial_data:
            return Event.objects.create(**validated_data)
        members = validated_data.pop("members")
        event = Event.objects.create(**validated_data)
        for member in members:
            current_member = User.objects.get(**member)
            EventMember.objects.create(event=event, member=current_member)
        return event

    def update(self, instance, validated_data):
        """Обновление мероприятия с указанными участниками."""
        if "members" not in self.initial_data:
            members = validated_data.pop("members")
        for member in members:
            current_member = User.objects.get(**member)
            EventMember.objects.create(event=instance, member=current_member)
        return super().update(instance, validated_data)
