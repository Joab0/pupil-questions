from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGINT NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL,
    "last_name" VARCHAR(30) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "verification_code" CHAR(36),
    "verification_expires_at" TIMESTAMP,
    "is_verified" INT NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "topic" (
    "id" BIGINT NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(1024) NOT NULL,
    "details" TEXT,
    "ai_status" VARCHAR(7) NOT NULL DEFAULT 'idle' /* IDLE: idle\nPENDING: pending\nDONE: done\nERROR: error */,
    "ai_requested_at" TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "question" (
    "id" BIGINT NOT NULL PRIMARY KEY,
    "question_text" TEXT NOT NULL,
    "options" JSON NOT NULL,
    "correct_answer" VARCHAR(1) NOT NULL,
    "explanation" TEXT NOT NULL,
    "topic_id" BIGINT NOT NULL REFERENCES "topic" ("id") ON DELETE CASCADE
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
