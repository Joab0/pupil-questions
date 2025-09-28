from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("components/nav_link.html", takes_context=True)
def nav_link(context, icon_name, label, path_name):
    request = context["request"]
    url = reverse(path_name)
    active = " active" if request.path == url else ""
    return {
        "icon_name": icon_name,
        "label": label,
        "url": url,
        "active": active,
    }


@register.inclusion_tag("components/menu.html", takes_context=True)
def menu(context):
    return context
