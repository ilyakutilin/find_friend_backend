import enum
from itertools import groupby
from typing import NamedTuple, Sequence

from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from rest_framework import serializers


def set_request_server(result, generator, request, public):
    """Установка адреса сервера для Swagger."""
    if request:
        url = request.build_absolute_uri("/api/v1/")
        result.setdefault("servers", []).append({"url": url})
    return result


class Attr(enum.Enum):
    """Список атрибутов для Swagger."""

    NON_FIELD_ERRORS = "non_field_errors"
    EMAIL = "email"
    PASSWORD = "password"


class Code(enum.Enum):
    """Список кодов ошибок для Swagger."""

    INVALID = "invalid"
    BLANK = "blank"
    INVALID_CREDENTIALS = "invalid_credentials"


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
