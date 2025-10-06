from datetime import timedelta

from babel.dates import format_timedelta
from django import template

register = template.Library()


@register.filter
def naturaldelta(value: timedelta) -> str:
    return format_timedelta(value, locale="pt_BR")
