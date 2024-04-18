import enum
from itertools import groupby
from typing import NamedTuple, Sequence

from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from drf_standardized_errors.handler import (
    exception_handler as standardized_errors_handler,
)
from drf_standardized_errors.openapi import AutoSchema
from rest_framework import serializers


class CustomAutoSchema(AutoSchema):
    """Кастомная схема для Swagger с удаленными parse errors."""

    def _should_add_error_response(
        self, responses: dict, status_code: str
    ) -> bool:
        if (
            status_code == "400"
            and status_code not in responses
            and self.view.get_exception_handler()
            is standardized_errors_handler
        ):
            # Исключаем parse errors из процесса принятия решения о включении
            # ошибок с кодом 400 в документацию
            return self._should_add_validation_error_response()
        return super()._should_add_error_response(responses, status_code)

    def _get_http400_serializer(self):
        # Убираем всю логику, связанную с parse errors
        return self._get_serializer_for_validation_error_response()


def set_request_server(result, generator, request, public):
    """Установка адреса сервера для Swagger."""
    if request:
        url = request.build_absolute_uri("/api/v1/")
        result.setdefault("servers", []).append({"url": url})
    return result


class Attr(enum.Enum):
    """Список атрибутов для Swagger."""

    NULL = None
    NON_FIELD_ERRORS = "non_field_errors"
    EMAIL = "email"
    PASSWORD = "password"
    CITY = "city"
    NAME = "name"
    DESCRIPTION = "description"
    EVENT_TYPE = "event_type"
    START_DATE = "start_date"
    MEMBERS_COUNT = "members_count"
    MIN_AGE = "min_age"
    MAX_AGE = "max_age"
    MIN_COUNT_MEMBERS = "min_count_members"
    MAX_COUNT_MEMBERS = "max_count_members"
    EVENT_PRICE = "event_price"
    IMAGE = "image"
    ADDRESS = "address"
    INTERESTS = "interests"
    SEX = "sex"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    BIRTHDAY = "birthday"


class Code(enum.Enum):
    """Список кодов ошибок для Swagger."""

    INVALID = "invalid"
    BLANK = "blank"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    USER_NOT_FRIEND = "user_not_friend"
    INVALID_CHOICE = "invalid_choice"
    REQUIRED = "required"
    DOES_NOT_EXIST = "does_not_exist"
    MAX_DIGITS = "max_digits"
    MIN_VALUE = "min_value"
    MAX_LENGTH = "max_length"
    CANNOT_CREATE_USER = "cannot_create_user"
    INVALID_USER_FIRST_NAME = "invalid_user_first_name"
    INVALID_USER_LAST_NAME = "invalid_user_last_name"


class ErrorExample(NamedTuple):
    """Схема ошибки для Swagger."""

    attr: Attr
    code: Code
    detail: str


class ValidationErrorSerializer(serializers.Serializer):
    """Схема ошибки валидации для Swagger."""

    attr = serializers.CharField()
    code = serializers.CharField()
    detail = serializers.CharField()


class ValidationErrorListSerializer(serializers.Serializer):
    """Схема списка ошибок валидации определенного типа для Swagger."""

    type_ = serializers.CharField(source="type")
    errors = ValidationErrorSerializer(many=True, read_only=True)


def make_response(
    error_examples: Sequence[ErrorExample],
    error_serializer: serializers.Serializer = ValidationErrorListSerializer,
) -> OpenApiResponse:
    """Создание схемы ответа для Swagger."""
    sorted_error_examples = sorted(error_examples, key=lambda x: x.code.value)
    grouped_errors = groupby(sorted_error_examples, key=lambda x: x.code.value)
    grouped_examples = []

    for code, examples in grouped_errors:
        example_obj = OpenApiExample(
            name=code,
            value={
                "type": "validation_error",
                "errors": [
                    {
                        "attr": e.attr.value,
                        "code": e.code.value,
                        "detail": e.detail,
                    }
                    for e in examples
                ],
            },
        )
        grouped_examples.append(example_obj)

    return OpenApiResponse(
        response=error_serializer,
        examples=grouped_examples,
    )
