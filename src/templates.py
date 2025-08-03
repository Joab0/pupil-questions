from fastapi.templating import Jinja2Templates

from .flash import get_flashed_message

templates = Jinja2Templates(directory="src/templates")
templates.env.globals["get_flashed_message"] = get_flashed_message
