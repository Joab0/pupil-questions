from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuestionSetAddForm
from .models import Question, QuestionSet
from .tasks import generate_questions_task


@login_required
def question_sets_view(request: HttpRequest):
    question_sets = QuestionSet.objects.filter(user=request.user)
    return render(
        request,
        "questions/question_sets.html",
        context={"title": "Minhas Questões", "question_sets": question_sets},
    )


@login_required
def add_question_set_view(request: HttpRequest):
    if request.method == "POST":
        form = QuestionSetAddForm(request.POST)
        if form.is_valid():
            # Checks if the user has pending question set.
            # Each user can only generate one set of questions at a time
            pending = QuestionSet.objects.filter(user=request.user, status="pending").exists()
            if pending:
                messages.error(
                    request, "Você já tem questões sendo geradas no momento, por favor, aguarde."
                )
            else:
                data = form.cleaned_data
                question_set = QuestionSet.objects.create(
                    user=request.user,
                    title=data["title"],
                    prompt=data["prompt"],
                    status="pending",
                )
                question_set.save()

                # Generate questions in a background task
                # Use on_commit hook to avoid task run before save
                transaction.on_commit(
                    lambda: generate_questions_task.delay(
                        question_set.pk, data["prompt"], data["questions_number"]
                    ),
                )
                messages.success(
                    request,
                    "O conjunto de questões foi criado com sucesso. "
                    "Aguarde até que as questões sejam geradas.",
                )
                return redirect("question_set", question_set_id=question_set.pk)
        else:
            messages.error(request, "Não foi possível criar o conjunto de questões.")
    else:
        form = QuestionSetAddForm()

    return render(
        request,
        "questions/add_question_set.html",
        context={"title": "Criar Questões", "form": form},
    )


@login_required
def question_set_view(request: HttpRequest, question_set_id: int):
    question_set = get_object_or_404(
        QuestionSet.objects.prefetch_related(
            Prefetch("questions", queryset=Question.objects.prefetch_related("choices"))
        ),
        pk=question_set_id,
        user=request.user,
    )

    return render(
        request,
        "questions/question_set.html",
        context={"title": question_set.title, "question_set": question_set},
    )


@login_required
def question_set_delete_view(request: HttpRequest, question_set_id: int):
    if request.method == "POST":
        question_set = get_object_or_404(QuestionSet, user=request.user, pk=question_set_id)
        question_set.delete()
    return redirect("question_sets")


@login_required
def question_set_status_view(request: HttpRequest, question_set_id: int):
    question_set = get_object_or_404(QuestionSet, user=request.user, pk=question_set_id)
    return JsonResponse({"status": question_set.status})
