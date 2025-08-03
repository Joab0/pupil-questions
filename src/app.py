from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .database.models import init_db_models
from .flash import flash
from .settings import settings
from .views.account import router as account_router
from .views.auth import router as auth_router
from .views.home import router as home_router
from .views.todo import router as todo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init db
    await init_db_models()
    yield


app = FastAPI(
    debug=settings.ENVIRONMENT == "development",
    docs_url=None,
    openapi_url=None,
    lifespan=lifespan,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=7 * 60 * 60 * 24,  # 7 days
)

# Routes setup
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(todo_router)
app.include_router(account_router)

app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def login_required_exception_handler(request: Request, _) -> RedirectResponse:
    flash(request, "Você precisa estar logado para acessar.", "danger")
    return RedirectResponse(request.url_for("login"), status.HTTP_303_SEE_OTHER)
