from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from ..database.models import Todo
from ..deps import CurrentUser
from ..flash import flash
from ..templates import templates

router = APIRouter()


@router.get("/todos")
async def get_todos(request: Request, user: CurrentUser):
    todos = await Todo.filter(user_id=user.id).order_by("checked", "created_at").all()

    return templates.TemplateResponse(
        request=request,
        name="todos.html.jinja",
        context={
            "title": "Lista de tarefas",
            "user": user,
            "todos": todos,
        },
    )


@router.post("/todos")
async def post_todos(
    request: Request,
    user: CurrentUser,
    task: Annotated[str, Form(min_length=2, max_length=255)],
):
    await Todo.create(user=user, task=task)
    flash(request, "Tarefa adicionada com sucesso", "success")
    return RedirectResponse(request.url_for("get_todos"), status.HTTP_303_SEE_OTHER)


@router.post("/todos/{id}/toggle")
async def toggle_todo(
    request: Request,
    user: CurrentUser,
    id: int,
):
    todo = await Todo.get(id=id)
    todo.checked = not todo.checked
    await todo.save()

    return RedirectResponse(request.url_for("get_todos"), status.HTTP_303_SEE_OTHER)


@router.post("/todos/{id}/delete")
async def delete_todo(
    request: Request,
    user: CurrentUser,
    id: int,
):
    todo = await Todo.get(id=id)
    await todo.delete()
    flash(request, "Tarefa removida com sucesso", "success")
    return RedirectResponse(request.url_for("get_todos"), status.HTTP_303_SEE_OTHER)
