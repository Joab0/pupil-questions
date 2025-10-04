from django.contrib import admin

from .models import Choice, PracticeAnswer, PracticeSession, Question, QuestionSet


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(PracticeAnswer)
class PracticeAnswerAdmin(admin.ModelAdmin):
    pass
