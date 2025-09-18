from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import EmailStr

from ..deps import CurrentUser
from ..flash import flash
from ..security import hash_password, verify_password
from ..templates import templates

router = APIRouter()


@router.get("/account")
async def get_account(request: Request, user: CurrentUser):
    if not user.is_verified:
        flash(
            request, "Você precisa verificar seu endereço de e-mail para usar sua conta.", "warning"
        )
    return templates.TemplateResponse(
        request=request,
        name="account.html.jinja",
        context={"title": "Sua conta", "user": user},
    )


@router.post("/account")
async def post_account(
    request: Request,
    user: CurrentUser,
    name: Annotated[str, Form(min_length=2)],
    last_name: Annotated[str, Form(min_length=2)],
    email: Annotated[EmailStr, Form()],
):
    name = name
    last_name = last_name

    user.name = name
    user.last_name = last_name

    if email != user.email:
        user.verification_code = uuid4()
        user.verification_expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        user.is_verified = False

    user.email = email

    await user.save()

    flash(request, "Suas informações foram salvas com sucesso!", "success")

    return RedirectResponse(request.url_for("get_account"), status.HTTP_303_SEE_OTHER)


@router.post("/account/password")
async def account_password(
    request: Request,
    user: CurrentUser,
    password: Annotated[str, Form()],
    new_password: Annotated[str, Form(min_length=8)],
    confirm_new_password: Annotated[str, Form(min_length=8)],
):
    if not verify_password(password, user.password):
        flash(
            request,
            "Não foi possível alterar a senha: a senha atual informada está incorreta.",
            "danger",
        )
        return RedirectResponse(request.url_for("get_account"), status.HTTP_303_SEE_OTHER)

    if new_password != confirm_new_password:
        flash(
            request,
            "As senhas não conferem. Verifique e tente novamente.",
            "danger",
        )
        return RedirectResponse(request.url_for("get_account"), status.HTTP_303_SEE_OTHER)

    user.password = hash_password(new_password)
    await user.save()

    flash(request, "Sua senha foi atualizada com sucesso!", "success")

    return RedirectResponse(request.url_for("get_account"), status.HTTP_303_SEE_OTHER)
