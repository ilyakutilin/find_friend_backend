from http import HTTPStatus

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.views import EventViewSet
from config.constants import messages as msg
from config.schema import Attr, Code, ErrorExample, make_response


class FixEventViewSet(OpenApiViewExtension):
    """Фикс документации OpenAPI для EventViewSet."""

    target_class = "api.views.EventViewSet"

    def view_replacement(self):
        """Расширение схемы для EventViewSet."""
        error_examples_list = (
            ErrorExample(
                Attr.CITY, Code.INVALID_CHOICE, msg.INVALID_CHOICE_MSG
            ),
        )
        error_examples_create = (
            [
                ErrorExample(attr, Code.REQUIRED, msg.FIELD_REQUIRED_MSG)
                for attr in (Attr.NAME, Attr.DESCRIPTION, Attr.EVENT_TYPE)
            ]
            + [
                ErrorExample(attr, Code.BLANK, msg.FIELD_CANNOT_BE_BLANK_MSG)
                for attr in (Attr.NAME, Attr.DESCRIPTION, Attr.EVENT_TYPE)
            ]
            + [
                ErrorExample(attr, Code.INVALID, msg.ENTER_CORRECT_INTEGER_MSG)
                for attr in (
                    Attr.MEMBERS_COUNT,
                    Attr.MIN_AGE,
                    Attr.MAX_AGE,
                    Attr.MIN_COUNT_MEMBERS,
                    Attr.MAX_COUNT_MEMBERS,
                )
            ]
            + [
                ErrorExample(attr, Code.MIN_VALUE, msg.MIN_VALUE_MSG)
                for attr in (
                    Attr.MIN_AGE,
                    Attr.MAX_AGE,
                    Attr.MIN_COUNT_MEMBERS,
                    Attr.MAX_COUNT_MEMBERS,
                )
            ]
            + [
                ErrorExample(
                    attr,
                    Code.MAX_LENGTH,
                    msg.MAX_CHARACTERS_MSG,
                )
                for attr in (Attr.NAME, Attr.EVENT_TYPE, Attr.ADDRESS)
            ]
            + [
                ErrorExample(
                    Attr.START_DATE,
                    Code.INVALID,
                    msg.INVALID_DATETIME_FORMAT_MSG,
                ),
                ErrorExample(
                    Attr.CITY, Code.DOES_NOT_EXIST, msg.PK_DOES_NOT_EXIST_MSG
                ),
                ErrorExample(
                    Attr.EVENT_PRICE,
                    Code.INVALID,
                    msg.VALID_NUMBER_IS_REQUIRED_MSG,
                ),
                ErrorExample(Attr.IMAGE, Code.INVALID, msg.INVALID_FILE_MSG),
                ErrorExample(
                    Attr.EVENT_PRICE, Code.MAX_DIGITS, msg.MAX_DIGITS_MSG
                ),
            ]
        )

        @extend_schema_view(
            list=extend_schema(
                summary="Список мероприятий",
                responses={
                    HTTPStatus.OK: EventViewSet.serializer_class(many=True),
                    HTTPStatus.BAD_REQUEST: make_response(error_examples_list),
                },
            ),
            create=extend_schema(
                summary="Создание мероприятия",
                responses={
                    HTTPStatus.BAD_REQUEST: make_response(
                        error_examples_create
                    ),
                },
            ),
            retrieve=extend_schema(
                summary="Просмотр мероприятия",
            ),
            update=extend_schema(
                summary="Обновление мероприятия",
                responses={
                    HTTPStatus.BAD_REQUEST: make_response(
                        error_examples_create
                    ),
                },
            ),
            partial_update=extend_schema(
                summary="Частичное обновление мероприятия",
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
            destroy=extend_schema(summary="Удаление мероприятия"),
            distance=extend_schema(
                summary=EventViewSet.distance.__doc__.rstrip("."),
            ),
            distances=extend_schema(
                summary=EventViewSet.distances.__doc__.rstrip("."),
            ),
            geolocation=extend_schema(
                summary=EventViewSet.geolocation.__doc__.rstrip("."),
            ),
        )
        class Fixed(self.target_class):
            pass

        return Fixed
