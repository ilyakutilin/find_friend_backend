from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Django Users App Config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        """Импорт схемы для работы расширений drf-spectacular."""
        import users.schema  # noqa: E402, F401
