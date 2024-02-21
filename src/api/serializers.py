from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, SlugRelatedField

# from events.models import EventInterest
from events.models import Event, EventMember
from users.models import City, Friend, Interest, User, UserInterest


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

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "sex",
            "age",
            # "email",
            "interests",
            "city",
            "interests",
            "avatar",
            "profession",
            "character",
            "purpose",
            "network_nick",
            "additionally",
        )

    def update(self, instance, validated_data):
        """Обновление пользователя с указанными интересами и городом."""
        interests = validated_data.pop("interests", None)
        if not instance:
            instance = User.objects.create(**validated_data)
        if interests:
            for interest in interests:
                try:
                    current_interest = Interest.objects.get(**interest)
                except Interest.DoesNotExist:
                    raise ValidationError(
                        "Пожалуйста, выберите интересы из списка "
                        "предустановленных."
                    )
                UserInterest.objects.update_or_create(
                    user=instance, interest=current_interest
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
            "location",
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
