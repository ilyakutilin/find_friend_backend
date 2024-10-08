from http import HTTPStatus

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema

from chat.serializers import ChatListSerializer, ChatSerializer
from chat.views import chats, get_chat, start_chat
from config.constants import messages as msg
from config.schema import Attr, Code, ErrorExample, make_response


class FixStartChatView(OpenApiViewExtension):
    """Фикс документации OpenAPI для view-функции открытия нового чата."""

    target_class = "chat.views.start_chat"

    def view_replacement(self):
        """Расширение схемы для view-функции start_chat."""
        error_examples = (
            ErrorExample(
                Attr.NULL,
                Code.USER_NOT_FOUND,
                msg.CANNOT_START_CHAT_WITH_NONEXISTENT_USER,
            ),
            ErrorExample(
                Attr.NULL, Code.USER_NOT_FRIEND, msg.USER_IS_NOT_FRIEND
            ),
        )
        return extend_schema(
            summary=start_chat.__doc__.rstrip("."),
            request=ChatSerializer,
            responses={
                HTTPStatus.OK: ChatSerializer,
                HTTPStatus.BAD_REQUEST: make_response(error_examples),
            },
        )(self.target_class)


class FixGetChatView(OpenApiViewExtension):
    """Фикс документации OpenAPI для view-функции просмотра чата."""

    target_class = "chat.views.get_chat"

    def view_replacement(self):
        """Расширение схемы для view-функции get_chat."""
        return extend_schema(
            summary=get_chat.__doc__.rstrip("."),
            request=ChatSerializer,
            responses={
                HTTPStatus.OK: ChatSerializer,
            },
        )(self.target_class)


class FixChatsView(OpenApiViewExtension):
    """Фикс документации OpenAPI для view-функции просмотра списка чатов."""

    target_class = "chat.views.chats"

    def view_replacement(self):
        """Расширение схемы для view-функции chats."""
        return extend_schema(
            summary=chats.__doc__.rstrip("."),
            responses={
                HTTPStatus.OK: ChatListSerializer(many=True),
            },
        )(self.target_class)
