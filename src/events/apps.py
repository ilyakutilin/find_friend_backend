from django.apps import AppConfig


class EventsConfig(AppConfig):
    """Django API App Config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        """Импорт схемы для работы расширений drf-spectacular."""
        import events.schema  # noqa: E402, F401
