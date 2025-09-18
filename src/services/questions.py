import json
from typing import Annotated, cast

from openai import AsyncClient
from pydantic import BaseModel, Field

from ..settings import settings

client = AsyncClient(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)


class Question(BaseModel):
    question: str
    options: dict[Annotated[str, Field(max_length=1)], str]
    correct: Annotated[str, Field(max_length=1)]
    explanation: str


class GenerateTopicQuestionsResponse(BaseModel):
    title: str
    description: str | None
    questions: list[Question]


async def generate_questions(topic: str, count: int) -> GenerateTopicQuestionsResponse:
    system_prompt = """
    You are a helpful assistant specialized in creating educational
    multiple-choice questions in Portuguese.
    Ensure questions are clear, concise, and accurate.
    """

    prompt = f"""Generate {count} multiple-choice questions on the topic "{topic}" in Portuguese.
    Each question must include:
    - A clear question statement
    - 4 answer options labeled A, B, C, and D
    - Indication of the correct answer option
    - Explanation
    Respond in JSON format, like this:
    The output must be a single compact JSON string without any extra formatting,
    line breaks or code blocks, just send the plain json, like this:
    {{
        "title": "Short name for this topic.",
        "description": "Optional description for this topic.",
        "questions": [
            {{
                "question": "...",
                "options": {{
                    "A": "...",
                    "B": "...",
                    "C": "...",
                    "D": "..."
                }},
                "correct": "B",
                "explanation": "..."
            }}
        ]
    }}
    """
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=1.5,
        stream=False,
    )
    text = cast(str, response.choices[0].message.content)
    data = json.loads(text)
    questions = [Question(**d) for d in data["questions"]]
    return GenerateTopicQuestionsResponse(
        title=data["title"],
        description=data["description"],
        questions=questions,
    )
