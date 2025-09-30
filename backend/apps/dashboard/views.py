from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from apps.questions.models import QuestionSet


@login_required
def dashboard_view(request: HttpRequest):
    questions_count = QuestionSet.objects.filter(user=request.user).count()
    return render(
        request,
        "dashboard/dashboard.html",
        context={"questions_count": questions_count},
    )
