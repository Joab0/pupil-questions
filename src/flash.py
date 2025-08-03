from fastapi import Request


def flash(request: Request, message: str, category: str = "") -> None:
    request.session["_message"] = {"message": message, "category": category}


def get_flashed_message(request: Request):
    return request.session.pop("_message", None)
