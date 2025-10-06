from django.contrib import admin

from apps.common.admin import BaseDBModelAdmin

from .models import Choice, PracticeAnswer, PracticeSession, Question, QuestionSet


@admin.register(QuestionSet)
class QuestionSetAdmin(BaseDBModelAdmin):
    list_display = ["id", "title", "user", "description", "created_at", "prompt", "model", "status"]


@admin.register(Question)
class QuestionAdmin(BaseDBModelAdmin):
    list_display = ["id", "question_set", "text", "type", "explanation"]


@admin.register(Choice)
class ChoiceAdmin(BaseDBModelAdmin):
    list_display = ["id", "question", "text", "is_correct"]


@admin.register(PracticeSession)
class PracticeSessionAdmin(BaseDBModelAdmin):
    list_display = ["id", "question_set", "created_at", "current_index", "finished_at"]


@admin.register(PracticeAnswer)
class PracticeAnswerAdmin(BaseDBModelAdmin):
    list_display = ["id", "session", "question", "choice"]
