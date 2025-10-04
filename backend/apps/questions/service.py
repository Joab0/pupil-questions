import json
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

    return GenerateQuestionSetResponse(**data)
