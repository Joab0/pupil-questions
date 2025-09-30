import string

from django import template

register = template.Library()


# Helper function to get a letter by index
# 0 -> A
# 1 -> B
@register.filter
def index_letter(index: int) -> str:
    return string.ascii_letters[index]
