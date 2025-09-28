from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# Helper function to user Bootstrap icons
@register.simple_tag
def icon(name: str, class_name: str = "") -> str:
    class_attr = f" {class_name.strip()}" if class_name else ""
    return mark_safe(f'<i class="bi bi-{name}{class_attr}"></i>')
