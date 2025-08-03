from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request

from .database.models import User


async def get_current_user(request: Request) -> User:
    user_id: Any | None = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")

    user = await User.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
