import logging

from celery import shared_task
from django.conf import settings
from django.db import transaction

from .models import Choice, Question, QuestionSet
from .service import generate_questions

log = logging.getLogger(__name__)


@shared_task(max_retries=0)
def generate_questions_task(question_set_id: int, prompt: str, questions_number: int) -> None:
    log.info(f"Generate questions task started for question set {question_set_id}")

    question_set = QuestionSet.objects.get(pk=question_set_id)

    try:
        response = generate_questions(prompt, questions_number)
        question_set.title = response.title
        question_set.model_name = settings.AI_SERVICE_MODEL
        question_set.save(update_fields=["title", "model_name"])

        with transaction.atomic():
            for question in response.questions:
                _question = Question.objects.create(
                    question_set=question_set,
                    text=question.text,
                    type="multiple_choice",
                    explanation=question.explanation,
                )
                for choice in question.choices:
                    Choice.objects.create(
                        question=_question,
                        text=choice.text,
                        is_correct=choice.is_correct,
                    )
        question_set.status = "success"
    except Exception as e:
        log.exception(f"Error generating questions for {question_set_id}: {e}")
        question_set.status = "error"

    question_set.save(update_fields=["status"])
