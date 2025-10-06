from django.apps import AppConfig
from django.urls import register_converter

from apps.common.converters import ULIDConverter


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self) -> None:
        register_converter(ULIDConverter, "ulid")
        return super().ready()
