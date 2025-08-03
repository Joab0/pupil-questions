from ..settings import settings

TORTOISE_ORM = {
    "connections": {"default": str(settings.DATABASE_URL)},
    "apps": {
        "models": {
            "models": ["src.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
