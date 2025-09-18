import logging
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Path, Request, status
from fastapi.responses import RedirectResponse
from tortoise.transactions import in_transaction

from ..database.models import Question, Topic
from ..deps import CurrentUser
from ..enums import AIRequestStatus
from ..flash import flash
from ..services.questions import generate_questions
from ..templates import templates

log = logging.getLogger(__name__)

router = APIRouter()


async def _get_topic(user: CurrentUser, id: Annotated[int, Path()]) -> Topic:
    topic = await Topic.get(user=user, id=id).prefetch_related("user", "questions")
    return topic


TopicDep = Annotated[Topic, Depends(_get_topic)]


@router.get("/topics")
async def get_topics(request: Request, user: CurrentUser):
    topics = await Topic.filter(user=user)
    topics = topics

    return templates.TemplateResponse(
        request=request,
        name="topics.html.jinja",
        context={"title": "Suas Questões", "user": user, "topics": topics},
    )


@router.get("/topics/{id}")
async def get_topic(request: Request, topic: TopicDep):
    # TODO: Check the AI status and request date to cancel the pending status.
    return templates.TemplateResponse(
        request=request,
        name="topic.html.jinja",
        context={"title": topic.name, "user": topic.user, "topic": topic},
    )


@router.post("/topics")
async def post_topics(
    request: Request,
    user: CurrentUser,
    name: Annotated[str, Form(min_length=2, max_length=255)],
    description: Annotated[str | None, Form(max_length=1024)],
):
    topic = await Topic.create(user=user, name=name, description=description)

    return RedirectResponse(request.url_for("get_topic", id=topic.id), status.HTTP_303_SEE_OTHER)


@router.get("/topics/{id}/edit")
async def edit_topic(request: Request, topic: TopicDep):
    return templates.TemplateResponse(
        request=request,
        name="edit_topic.html.jinja",
        context={"title": topic.name, "user": topic.user, "topic": topic},
    )


@router.post("/topics/{id}/edit")
async def post_edit_topic(
    request: Request,
    topic: TopicDep,
    name: Annotated[str, Form(min_length=2, max_length=100)],
    description: Annotated[str | None, Form(max_length=1024)],
):
    topic.name = name
    topic.description = description or None  # pyright: ignore[reportAttributeAccessIssue]
    await topic.save()
    flash(request, "Informações atualizadas com sucesso!", "success")
    return RedirectResponse(request.url_for("get_topic", id=topic.id), status.HTTP_303_SEE_OTHER)


@router.post("/topics/{id}/delete")
async def delete_topic(request: Request, topic: TopicDep):
    await topic.delete()
    flash(request, f'O tópico "{topic.name}" foi deletado com sucesso!', "success")
    return RedirectResponse(request.url_for("get_topics"), status.HTTP_303_SEE_OTHER)


@router.post("/topics/{id}/create-question")
async def create_question(
    request: Request,
    topic: TopicDep,
    question_text: Annotated[str, Form(min_length=2, max_length=1024)],
    option_a: Annotated[str, Form(min_length=1, max_length=1024)],
    option_b: Annotated[str, Form(min_length=1, max_length=1024)],
    option_c: Annotated[str, Form(min_length=1, max_length=1024)],
    option_d: Annotated[str, Form(min_length=1, max_length=1024)],
    correct_answer: Annotated[Literal["A", "B", "C", "D"], Form()],
    explanation: Annotated[str, Form(max_length=1024)],
):
    await Question.create(
        topic=topic,
        question_text=question_text,
        options={
            "A": option_a,
            "B": option_b,
            "C": option_c,
            "D": option_d,
        },
        correct_answer=correct_answer,
        explanation=explanation,
    )
    flash(request, "A questão foi adicionada com sucesso.", "success")
    return RedirectResponse(request.url_for("edit_topic", id=topic.id), status.HTTP_303_SEE_OTHER)


async def _get_question(user: CurrentUser, id: Annotated[int, Path()]) -> Question:
    question = await Question.get(topic__user=user, id=id).prefetch_related("topic")
    return question


QuestionDep = Annotated[Question, Depends(_get_question)]


@router.post("/questions/{id}/edit")
async def edit_question(
    request: Request,
    question: QuestionDep,
    question_text: Annotated[str, Form(min_length=2, max_length=1024)],
    option_a: Annotated[str, Form(min_length=1, max_length=1024)],
    option_b: Annotated[str, Form(min_length=1, max_length=1024)],
    option_c: Annotated[str, Form(min_length=1, max_length=1024)],
    option_d: Annotated[str, Form(min_length=1, max_length=1024)],
    correct_answer: Annotated[Literal["A", "B", "C", "D"], Form()],
    explanation: Annotated[str, Form(max_length=1024)],
):
    question.question_text = question_text
    question.options = {
        "A": option_a,
        "B": option_b,
        "C": option_c,
        "D": option_d,
    }

    question.correct_answer = correct_answer
    question.explanation = explanation
    await question.save()

    flash(request, "A questão foi atualizada com sucesso.", "success")
    return RedirectResponse(
        request.url_for("edit_topic", id=question.topic.id), status.HTTP_303_SEE_OTHER
    )


@router.post("/questions/{id}/delete")
async def delete_question(request: Request, question: QuestionDep):
    await question.delete()
    flash(request, "A questão foi excluida com sucesso.", "success")
    return RedirectResponse(
        request.url_for("edit_topic", id=question.topic.id), status.HTTP_303_SEE_OTHER
    )


async def generate_topic_questions_task(topic: Topic, count: int) -> None:
    try:
        response = await generate_questions(topic.details, count=count)
        async with in_transaction():
            await Question.bulk_create(
                [
                    Question(
                        topic=topic,
                        question_text=question.question,
                        options=question.options,
                        correct_answer=question.correct,
                        explanation=question.explanation,
                    )
                    for question in response.questions
                ]
            )
        topic.name = response.title
        topic.description = response.description  # pyright: ignore[reportAttributeAccessIssue]
        topic.ai_status = AIRequestStatus.DONE
    except Exception:
        log.exception("Can't generate questions")
        topic.ai_status = AIRequestStatus.ERROR
    finally:
        await topic.save()


@router.post("/topics/{id}/generate-questions")
async def generate_topic_questions(
    request: Request,
    topic: TopicDep,
    details: Annotated[str, Form(min_length=10, max_length=2048)],
    count: Annotated[int, Form(ge=1, le=10)],
    background_tasks: BackgroundTasks,
):
    topic.details = details
    topic.ai_requested_at = datetime.now(timezone.utc)
    topic.ai_status = AIRequestStatus.PENDING
    await topic.save()

    background_tasks.add_task(generate_topic_questions_task, topic=topic, count=count)

    return RedirectResponse(request.url_for("get_topic", id=topic.id), status.HTTP_303_SEE_OTHER)
