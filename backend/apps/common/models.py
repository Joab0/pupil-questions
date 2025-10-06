from datetime import datetime

from django.db import models
from django_ulidfield import ULIDField
from ulid import ULID


class BaseDBModel(models.Model):
    id = ULIDField(primary_key=True)

    class Meta:
        abstract = True

    @property
    def created_at(self) -> datetime:
        return ULID().from_str(self.id).datetime
