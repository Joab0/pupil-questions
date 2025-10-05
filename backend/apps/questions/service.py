import json
import math
import random
from collections import defaultdict
from typing import cast

from django.conf import settings
from openai import Client
from pydantic import BaseModel

client = Client(
    api_key=settings.AI_SERVICE_API_KEY,
    base_url=settings.AI_SERVICE_BASE_URL,
)


class Choice(BaseModel):
    text: str
    is_correct: bool


class Question(BaseModel):
    text: str
    choices: list[Choice]
    explanation: str


class GenerateQuestionSetResponse(BaseModel):
    title: str
    description: str
    questions: list[Question]


def _shuffle_choices(questions: list[Question]) -> None:
    """Reorder the question choices.
    Keep the correct alternative of the question in a balanced index.
    Ex: if there are 20 questions with 4 choices each,
    the index of the correct choice will be 4x0, 4x1, 4x2,4x3 or 25% each.
    """

    num_choices = max(len(q.choices) for q in questions)
    indexes_count = defaultdict(int)
    max_per_index = math.ceil(len(questions) / num_choices)

    for question in questions:
        correct_choice = next(c for c in question.choices if c.is_correct)
        incorrect_choices = [c for c in question.choices if not c.is_correct]

        # Get the min used
        min_used = min(indexes_count.values(), default=0)
        available_indexes = [
            i
            for i in range(num_choices)
            if indexes_count[i] == min_used and indexes_count[i] < max_per_index
        ]

        # If all indexes are full, use any one
        if not available_indexes:
            available_indexes = list(range(num_choices))

        correct_index = random.choice(available_indexes)
        indexes_count[correct_index] += 1

        random.shuffle(incorrect_choices)
        new_order = []
        for i in range(num_choices):
            if i == correct_index:
                new_order.append(correct_choice)
            else:
                new_order.append(incorrect_choices.pop(0))

        question.choices = new_order


def generate_questions(prompt: str, count: int) -> GenerateQuestionSetResponse:
    system_prompt = """You are a helpful assistant specialized in creating educational
    multiple-choice questions in Portuguese (Brazil).
    Ensure questions are clear, concise, and accurate."""

    prompt = f"""Generate {count} multiple-choice questions basend on prompt "{prompt}".
    Each question must include:
    - A clear question statement
    - 4 answer options
    - Indication of the correct answer option
    - Explanation
    Respond in JSON format, like this:
    {{
        "title": "Short title",
        "description": "Short description",
        "questions": [
            {{
                "text": "...",
                "choices": [
                    {{"text": "choice text", "is_correct": true}},
                    ...
                ],
                "explanation": "..."
            }}
        ]
    }}
    """
    response = client.chat.completions.create(
        model=settings.AI_SERVICE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=1.3,
        stream=False,
    )
    text = cast(str, response.choices[0].message.content)
    data = json.loads(text)

    res = GenerateQuestionSetResponse(**data)
    _shuffle_choices(res.questions)
    return res
