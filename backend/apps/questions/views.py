import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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
                    # Temporary title
                    title=data["prompt"][:30],
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

    # Get current practice session
    active_practice_session = PracticeSession.objects.filter(
        question_set=question_set, finished_at=None
    ).first()

    return render(
        request,
        "questions/question_set.html",
        context={
            "title": question_set.title,
            "question_set": question_set,
            "active_practice_session": active_practice_session,
        },
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

    # Get current practice or create a new
    session, created = PracticeSession.objects.get_or_create(
        question_set=question_set,
        finished_at=None,
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

    return redirect("question_set_practice", question_set_id=question_set.pk, session_id=session.pk)


@login_required
def question_set_practice_view(request: HttpRequest, question_set_id: int, session_id: int):
    session = get_object_or_404(
        PracticeSession,
        id=session_id,
        question_set_id=question_set_id,
        question_set__user=request.user,
    )

    question_id = session.questions_order[session.current_index]
    question = Question.objects.prefetch_related("choices").get(pk=question_id)

    if request.method == "POST":
        choice_id = request.POST.get("choice")
        if choice_id is not None:
            PracticeAnswer.objects.update_or_create(
                session=session,
                question=question,
                defaults={"choice_id": choice_id},
            )

        if "next" in request.POST:
            session.current_index = min(session.current_index + 1, len(session.questions_order) - 1)
        elif "previous" in request.POST:
            session.current_index = max(session.current_index - 1, 0)
        elif "finish" in request.POST:
            # check if all questions have been answered
            unanswered_index = session.get_next_unanswered_index()
            if unanswered_index is not None:
                session.current_index = unanswered_index
                messages.error(request, "Por favor, responda essa questão antes de finalizar.")
            else:
                session.finished_at = timezone.now()
                session.save()
                return redirect(
                    "question_set_practice_results",
                    question_set_id=session.question_set.pk,
                    session_id=session.pk,
                )

        session.save()
        return redirect(
            "question_set_practice", question_set_id=session.question_set.pk, session_id=session.pk
        )

    answer = session.answers.filter(question=question).first()  # pyright: ignore[reportAttributeAccessIssue]
    selected_choice_id = answer.choice.pk if answer else None
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


@login_required
def question_set_practice_results_view(request: HttpRequest, question_set_id: int, session_id: int):
    session = get_object_or_404(
        PracticeSession.objects.exclude(
            finished_at__isnull=True,
        ).prefetch_related(
            Prefetch(
                "answers",
                queryset=PracticeAnswer.objects.prefetch_related("question"),
            ),
            Prefetch(
                "question_set",
                queryset=QuestionSet.objects.prefetch_related(
                    Prefetch(
                        "questions",
                        queryset=Question.objects.prefetch_related("choices"),
                    )
                ),
            ),
        ),
        pk=session_id,
        question_set_id=question_set_id,
    )
    answers = session.answers
    question_set = session.question_set

    duration = session.finished_at - session.created_at

    answers = {a.question.pk: a for a in session.answers.all()}

    results = []
    correct = 0
    for q_id in session.questions_order:
        question = next(q for q in question_set.questions.all() if q.pk == q_id)
        answer = answers[q_id]
        is_correct = answer.choice.is_correct

        if is_correct:
            correct += 1

        results.append(
            {
                "question": question,
                "selected_choice": answer.choice,
                "is_correct": is_correct,
            }
        )

    return render(
        request,
        "questions/practice_results.html",
        context={
            "title": "Resultados da prática",
            "session": session,
            "question_set": question_set,
            "duration": duration,
            "results": results,
            "stats": {
                "correct": correct,
                "total": len(results),
                "percent": correct / len(results) * 100,
            },
        },
    )
