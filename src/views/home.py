from fastapi import APIRouter, Request

from ..deps import CurrentUser
from ..templates import templates

router = APIRouter()


@router.get("/")
async def home(request: Request, user: CurrentUser):
    return templates.TemplateResponse(
        request=request,
        name="home.html.jinja",
        context={"title": "Página inicial", "user": user},
    )
