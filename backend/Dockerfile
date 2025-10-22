FROM python:3.13

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen --no-cache

WORKDIR /app/backend

COPY backend/ /app/backend/

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
