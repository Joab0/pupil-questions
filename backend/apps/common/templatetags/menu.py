from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.urls import reverse

from apps.questions.models import QuestionSet

if TYPE_CHECKING:
    pass


register = template.Library()


@register.inclusion_tag("components/nav_link.html", takes_context=True)
def nav_link(
    context: dict,
    label: str,
    path_name: str,
    icon_name: str | None = None,
):
    request = context["request"]
    if path_name.startswith("/"):
        url = path_name
    else:
        url = reverse(path_name)

    active = " active" if request.path == url else ""
    return {
        "label": label,
        "url": url,
        "icon_name": icon_name,
        "active": active,
    }


@register.inclusion_tag("components/nav_link.html", takes_context=True)
def question_set_nav_link(context: dict, question_set: QuestionSet):
    request = context["request"]

    url = reverse("question_set", kwargs={"question_set_id": question_set.id})
    actions = [
        {
            "icon": "pin-angle",
            "label": "Fixar" if question_set.pinned_at is None else "Desfixar",
            "url": reverse("question_set_toggle_pin", kwargs={"question_set_id": question_set.id}),
        },
        {
            "icon": "trash",
            "label": "Excluir",
            "url": reverse("question_set_delete", kwargs={"question_set_id": question_set.id}),
            "danger": True,
        },
    ]

    active = " active" if request.path == url else ""
    context = {
        "label": question_set.title,
        "url": url,
        "actions": actions,
        "active": active,
    }

    if question_set.pinned_at:
        context["icon_name"] = "pin-fill"

    return context


@register.inclusion_tag("components/menu.html", takes_context=True)
def menu(context):
    return context
