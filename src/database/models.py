import logging
from datetime import datetime, timezone

from snowflake import SnowflakeGenerator
from tortoise import Model, Tortoise, fields

from ..enums import AIRequestStatus
from .config import TORTOISE_ORM

log = logging.getLogger(__name__)

gen = SnowflakeGenerator(instance=1, epoch=1735700400)


class BaseModel(Model):
    id = fields.BigIntField(pk=True, generated=False, default=lambda: next(gen))

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        abstract = True

    @property
    def created_at(self) -> datetime:
        timestamp_ms = (self.id >> 22) + gen.epoch
        return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)


class User(BaseModel):
    name = fields.CharField(max_length=20)
    last_name = fields.CharField(max_length=30)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    updated_at = fields.DatetimeField(auto_now=True)

    verification_code = fields.UUIDField(null=True)
    verification_expires_at = fields.DatetimeField(null=True)
    is_verified = fields.BooleanField(default=False)

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.last_name}"


class Topic(BaseModel):
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=1024)
    details = fields.TextField(null=True)
    ai_status = fields.CharEnumField(AIRequestStatus, default=AIRequestStatus.IDLE)
    ai_requested_at = fields.DatetimeField(null=True)

    user = fields.ForeignKeyField("models.User", related_name="topics")
    questions: fields.ReverseRelation["Question"]


class Question(BaseModel):
    question_text = fields.TextField()
    options = fields.JSONField()
    correct_answer = fields.CharField(max_length=1)
    explanation = fields.TextField()

    topic = fields.ForeignKeyField("models.Topic", related_name="questions")


async def init_db_models():
    log.info("Connecting to database...")
    await Tortoise.init(config=TORTOISE_ORM)
    log.info("Successfully connected to database")
