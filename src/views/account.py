from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from ..deps import CurrentUser
from ..flash import flash
from ..security import hash_password, verify_password
from ..templates import templates

router = APIRouter()


@router.get("/account")
async def get_account(request: Request, user: CurrentUser):
    return templates.TemplateResponse(
        request=request,
        name="account.html.jinja",
        context={"user": user},
    )


@router.post("/account")
async def post_account(
    request: Request,
    user: CurrentUser,
    name: Annotated[str, Form(min_length=2)],
    last_name: Annotated[str, Form(min_length=2)],
    email: Annotated[str, Form(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")],
):
    name = name
    last_name = last_name

    user.name = name
    user.last_name = last_name
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
