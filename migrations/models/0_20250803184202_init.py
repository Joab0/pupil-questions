from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(20) NOT NULL,
    "last_name" VARCHAR(30) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "role" SMALLINT NOT NULL /* student: 0\nteacher: 1 */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "classroom" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT,
    "color" VARCHAR(7) NOT NULL,
    "invite_code" VARCHAR(100) NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "assignment" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "due_date" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "classroom_id" INT NOT NULL REFERENCES "classroom" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "chatmessage" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "message" TEXT NOT NULL,
    "sent_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "classroom_id" INT NOT NULL REFERENCES "classroom" ("id") ON DELETE CASCADE,
    "sender_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "enrollment" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "joined_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "classroom_id" INT NOT NULL REFERENCES "classroom" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "post" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "classroom_id" INT NOT NULL REFERENCES "classroom" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "todo" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "task" VARCHAR(255) NOT NULL,
    "checked" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
