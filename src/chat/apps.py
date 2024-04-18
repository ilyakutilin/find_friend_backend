from django.apps import AppConfig


class ChatConfig(AppConfig):
    """Chat app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "chat"

    def ready(self):
        """Импорт схемы для работы расширений drf-spectacular."""
        import chat.schema  # noqa: E402, F401
