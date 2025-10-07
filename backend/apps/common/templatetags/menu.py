from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("components/nav_link.html", takes_context=True)
def nav_link(context: dict, label: str, path_name: str, icon_name: str | None = None):
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


@register.inclusion_tag("components/menu.html", takes_context=True)
def menu(context):
    return context
