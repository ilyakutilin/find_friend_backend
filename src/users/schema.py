from http import HTTPStatus

from djoser.serializers import TokenSerializer
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import OpenApiResponse, extend_schema

from chat.serializers import ChatSerializer
from config.constants import messages as msg
from config.schema import Attr, Code, ErrorExample, make_response


class FixDjoserTokenCreateView(OpenApiViewExtension):
    """Фикс документации OpenAPI для djoser TokenCreateView."""

    target_class = "djoser.views.TokenCreateView"

    def view_replacement(self):
        """Расширение схемы для view-класса TokenCreateView."""
        error_examples = (
            ErrorExample(
                Attr.EMAIL, Code.BLANK, msg.FIELD_CANNOT_BE_BLANK_MSG
            ),
            ErrorExample(
                Attr.PASSWORD, Code.BLANK, msg.FIELD_CANNOT_BE_BLANK_MSG
            ),
            ErrorExample(
                Attr.NON_FIELD_ERRORS, Code.INVALID, msg.EMAIL_LENGTH_MSG
            ),
            ErrorExample(
                Attr.NON_FIELD_ERRORS, Code.INVALID, msg.EMAIL_ENGLISH_ONLY_MSG
            ),
            ErrorExample(
                Attr.NON_FIELD_ERRORS, Code.INVALID, msg.INVALID_EMAIL_MSG
            ),
            ErrorExample(
                Attr.NON_FIELD_ERRORS, Code.INVALID, msg.PASSWORD_LENGTH_MSG
            ),
            ErrorExample(
                Attr.NON_FIELD_ERRORS,
                Code.INVALID_CREDENTIALS,
                msg.INVALID_CREDENTIALS_MSG,
            ),
        )

        class Fixed(self.target_class):

            @extend_schema(
                summary="Вход в систему (создание токена аутентификации)",
                responses={
                    HTTPStatus.OK: TokenSerializer,
                    HTTPStatus.BAD_REQUEST: make_response(error_examples),
                },
            )
            def post(self, *args, **kwargs):
                """Вход в систему (создание токена аутентификации)."""
                return super().post(*args, **kwargs)

        return Fixed


class FixDjoserTokenDestroyView(OpenApiViewExtension):
    """Фикс документации OpenAPI для djoser TokenDestroyView."""

    target_class = "djoser.views.TokenDestroyView"

    def view_replacement(self):
        """Расширение схемы для view-класса TokenCreateView."""

        class Fixed(self.target_class):

            @extend_schema(
                summary="Выход из системы (удаление токена аутентификации)",
                request=ChatSerializer,
                responses={
                    HTTPStatus.NO_CONTENT: OpenApiResponse(
                        description="No Content",
                    ),
                    HTTPStatus.BAD_REQUEST: None,
                },
            )
            def post(self, *args, **kwargs):
                """Выход из системы (удаление токена аутентификации)."""
                return super().post(*args, **kwargs)

        return Fixed
