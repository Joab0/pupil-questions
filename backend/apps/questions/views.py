import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuestionSetAddForm
from .models import PracticeAnswer, PracticeSession, Question, QuestionSet
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


@login_required
def question_set_start_practice_view(request: HttpRequest, question_set_id: int):
    question_set = get_object_or_404(QuestionSet, pk=question_set_id, user=request.user)

    session, created = PracticeSession.objects.get_or_create(
        user=request.user,
        question_set=question_set,
        defaults={
            "questions_order": [],
            "current_index": 0,
        },
    )

    # No order or restart
    if created or not session.questions_order:
        questions = list(question_set.questions.values_list("pk", flat=True))  # pyright: ignore[reportAttributeAccessIssue]
        random.shuffle(questions)
        session.questions_order = questions
        session.current_index = 0
        session.save()

    return redirect("question_set_practice", session_id=session.pk)


@login_required
def question_set_practice_view(request: HttpRequest, session_id: int):
    session = get_object_or_404(
        PracticeSession.objects.prefetch_related("question_set"), pk=session_id, user=request.user
    )
    question_id = session.questions_order[session.current_index]
    question = Question.objects.prefetch_related("choices").get(pk=question_id)

    if request.method == "POST":
        choice_id = request.POST.get("choice")
        PracticeAnswer.objects.update_or_create(
            session=session, question=question, defaults={"choice_id": choice_id}
        )

        if "next" in request.POST:
            session.current_index = min(session.current_index + 1, len(session.questions_order) - 1)
        elif "previous" in request.POST:
            session.current_index = max(session.current_index - 1, 0)
        session.save()
        return redirect("question_set_practice", session_id=session.pk)

    answer = session.answers.filter(question=question).first()  # pyright: ignore[reportAttributeAccessIssue]
    selected_choice_id = answer.choice_id if answer else None
    progress = int(((session.current_index + 1) / len(session.questions_order)) * 100)

    return render(
        request,
        "questions/practice.html",
        context={
            "question": question,
            "session": session,
            "selected_choice_id": selected_choice_id,
            "progress": int(progress),
        },
    )
