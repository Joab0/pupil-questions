import logging

from tortoise import Model, Tortoise, fields

from ..enums import UserRole
from .config import TORTOISE_ORM

log = logging.getLogger(__name__)


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20)
    last_name = fields.CharField(max_length=30)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    role = fields.IntEnumField(UserRole)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    enrollments: fields.ReverseRelation["Enrollment"]
    posts: fields.ReverseRelation["Post"]
    assignments: fields.ReverseRelation["Assignment"]
    messages: fields.ReverseRelation["ChatMessage"]
    created_classes: fields.ReverseRelation["Classroom"]
    todos: fields.ReverseRelation["Todo"]

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.last_name}"

    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.teacher


class Classroom(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    color = fields.CharField(max_length=7, comment="Hex color code")
    invite_code = fields.CharField(max_length=100)
    created_by = fields.ForeignKeyField("models.User", related_name="created_classes")
    created_at = fields.DatetimeField(auto_now_add=True)

    enrollments: fields.ReverseRelation["Enrollment"]
    posts: fields.ReverseRelation["Post"]
    assignments: fields.ReverseRelation["Assignment"]
    messages: fields.ReverseRelation["ChatMessage"]


class Enrollment(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="enrollments")
    classroom = fields.ForeignKeyField("models.Classroom", related_name="enrollments")
    joined_at = fields.DatetimeField(auto_now_add=True)


class Post(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="posts")
    classroom = fields.ForeignKeyField("models.Classroom", related_name="posts")
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Assignment(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="assignments")  # Teacher
    classroom = fields.ForeignKeyField("models.Classroom", related_name="assignments")
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    due_date = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)


class ChatMessage(Model):
    id = fields.IntField(pk=True)
    sender = fields.ForeignKeyField("models.User", related_name="messages")
    classroom = fields.ForeignKeyField("models.Classroom", related_name="messages")
    message = fields.TextField()
    sent_at = fields.DatetimeField(auto_now_add=True)


class Todo(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="todos")  # Teacher
    task = fields.CharField(max_length=255)
    checked = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)


async def init_db_models():
    log.info("Connecting to database...")
    await Tortoise.init(config=TORTOISE_ORM)
    log.info("Successfully connected to database")
