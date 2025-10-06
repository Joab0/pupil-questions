import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_format(text):
    html = markdown.markdown(
        text or "",
        extensions=[
            "fenced_code",  # Allow ```code blocks```
            "codehilite",  # syntax highlight with Pygments
            "tables",
            "toc",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {
                "linenums": False,
                "css_class": "highlight",
            }
        },
        output_format="html",
    )

    # Apply Bootstrap styles
    html = html.replace("<table>", '<table class="table table-bordered">')

    return mark_safe(html)
