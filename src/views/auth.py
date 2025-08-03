from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from ..database.models import User
from ..enums import UserRole
from ..flash import flash
from ..security import hash_password, verify_password
from ..templates import templates

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html.jinja")


@router.post("/login")
async def post_login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = await User.get_or_none(email=email)

    if user is None or not verify_password(password, user.password):
        flash(request, "E-mail ou senha incorretos. Tente novamente", "danger")
        return RedirectResponse(request.url_for("login"), status.HTTP_303_SEE_OTHER)

    request.session["user_id"] = user.id

    return RedirectResponse(request.url_for("home"), status.HTTP_303_SEE_OTHER)


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="register.html.jinja")


@router.post("/register")
async def post_register(
    request: Request,
    name: Annotated[str, Form(min_length=2)],
    last_name: Annotated[str, Form(min_length=2)],
    email: Annotated[str, Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    role: Annotated[UserRole, Form()],
):
    if await User.exists(email=email):
        flash(request, "Já existe um usuário com este e-mail")
        return RedirectResponse(request.url_for("register"), status_code=status.HTTP_303_SEE_OTHER)

    # Sanitize data
    name = name
    last_name = last_name

    if len(password) < 8:
        flash(request, "A senha deve ter pelo menos 8 digitos")
        return RedirectResponse(request.url_for("register"), status_code=status.HTTP_303_SEE_OTHER)

    if password != confirm_password:
        flash(request, "As senhas não coincidem")
        return RedirectResponse(request.url_for("register"), status_code=status.HTTP_303_SEE_OTHER)

    # Create user
    user = await User.create(
        name=name,
        last_name=last_name,
        email=email,
        password=hash_password(password),
        role=role,
    )

    request.session["user_id"] = user.id

    return RedirectResponse(request.url_for("home"), status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(request.url_for("login"), status.HTTP_303_SEE_OTHER)
