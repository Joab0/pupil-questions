from django.contrib import admin

from .models import Choice, PracticeAnswer, PracticeSession, Question, QuestionSet


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "model", "created_at", "status"]
    readonly_fields = ["created_at"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_set", "text", "type", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["question", "text", "is_correct"]


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "question_set", "current_index", "created_at"]


@admin.register(PracticeAnswer)
class PracticeAnswerAdmin(admin.ModelAdmin):
    list_display = ["session", "question", "choice"]
