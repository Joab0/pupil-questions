from django.contrib import admin

from .models import Choice, Question, QuestionSet


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "model_name", "created_at", "status"]
    readonly_fields = ["created_at"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_set", "text", "type", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["question", "text", "is_correct"]
