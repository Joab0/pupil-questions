from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


def user_question_sets(request: HttpRequest):
    if request.user.is_authenticated:
        return {
            "user_question_sets": request.user.question_sets.order_by("-pinned_at", "-id").all()  # pyright: ignore
        }
    return {"user_question_sets": []}
