from http import HTTPStatus

from djoser.constants import Messages as DjoserMsg
from djoser.serializers import TokenSerializer
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)

from chat.serializers import ChatSerializer
from config.constants import messages as msg
from config.schema import Attr, Code, ErrorExample, make_response


class FixMyUserViewSet(OpenApiViewExtension):
    """Фикс документации OpenAPI для MyUserViewSet."""

    target_class = "api.views.MyUserViewSet"

    def view_replacement(self):
        """Расширение схемы для MyUserViewSet."""
        error_examples_list = [
            ErrorExample(attr, Code.INVALID_CHOICE, msg.INVALID_CHOICE_MSG)
            for attr in (Attr.CITY, Attr.INTERESTS, Attr.SEX)
        ]
        error_examples_create = (
            [
                ErrorExample(attr, Code.REQUIRED, msg.FIELD_REQUIRED_MSG)
                for attr in (
                    Attr.FIRST_NAME,
                    Attr.LAST_NAME,
                    Attr.EMAIL,
                    Attr.PASSWORD,
                )
            ]
            + [
                ErrorExample(attr, Code.BLANK, msg.FIELD_CANNOT_BE_BLANK_MSG)
                for attr in (
                    Attr.FIRST_NAME,
                    Attr.LAST_NAME,
                    Attr.EMAIL,
                    Attr.PASSWORD,
                )
            ]
            + [
                ErrorExample(Attr.BIRTHDAY, Code.INVALID, detail)
                for detail in (
                    msg.INVALID_BIRTHDAY,
                    msg.INVALID_DATETIME_FORMAT_MSG,
                )
            ]
            + [
                ErrorExample(
                    Attr.NON_FIELD_ERRORS,
                    Code.CANNOT_CREATE_USER,
                    DjoserMsg.CANNOT_CREATE_USER_ERROR,
                ),
                ErrorExample(
                    Attr.FIRST_NAME,
                    Code.INVALID_USER_FIRST_NAME,
                    msg.INVALID_SYMBOLS_MSG,
                ),
                ErrorExample(
                    Attr.LAST_NAME,
                    Code.INVALID_USER_LAST_NAME,
                    msg.INVALID_SYMBOLS_MSG,
                ),
                ErrorExample(Attr.EMAIL, Code.INVALID, msg.INVALID_EMAIL_MSG),
            ]
        )

        @extend_schema_view(
            list=extend_schema(
                summary="Список пользователей",
                responses={
                    HTTPStatus.BAD_REQUEST: make_response(error_examples_list)
                },
            ),
            create=extend_schema(
                summary="Создание пользователя",
                responses={
                    HTTPStatus.BAD_REQUEST: make_response(
                        error_examples_create
                    )
                },
            ),
            retrieve=extend_schema(
                summary="Просмотр пользователя",
            ),
            update=extend_schema(
                summary="Обновление пользователя",
                # responses={
                #     HTTPStatus.BAD_REQUEST: make_response(
                #         error_examples_create
                #     ),
                # },
            ),
            partial_update=extend_schema(
                summary="Частичное обновление пользователя",
                responses={
                    HTTPStatus.BAD_REQUEST: make_response(
                        [
                            ee
                            for ee in error_examples_create
                            if all(
                                (
                                    ee.code != Code.REQUIRED,
                                    ee.code != Code.BLANK,
                                )
                            )
                        ]
                    ),
                },
            ),
            destroy=extend_schema(summary="Удаление пользователя"),
        )
        class Fixed(self.target_class):
            pass

        return Fixed


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
