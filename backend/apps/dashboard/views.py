from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from apps.questions.models import PracticeSession, Question


@login_required
def dashboard_view(request: HttpRequest):
    questions_count = Question.objects.filter(question_set__user=request.user).count()
    practice_sessions = PracticeSession.objects.filter(question_set__user=request.user).all()
    practices_count = practice_sessions.count()

    practice_time = timedelta()
    for session in practice_sessions:
        if session.finished_at is None:
            continue

        practice_time += session.finished_at - session.created_at

    return render(
        request,
        "dashboard/dashboard.html",
        context={
            "questions_count": questions_count,
            "practices_count": practices_count,
            "practice_time": practice_time,
        },
    )
