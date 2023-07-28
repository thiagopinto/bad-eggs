from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "clients" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "client_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "responsible_name" VARCHAR(255) NOT NULL,
    "responsible_email" VARCHAR(255) NOT NULL,
    "client_secret_hash" VARCHAR(255),
    "verified_hash" VARCHAR(255),
    "verified_is" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "scopes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "username" VARCHAR(255) NOT NULL,
    "verified_hash" VARCHAR(255),
    "verified_is" BOOL NOT NULL  DEFAULT False,
    "password_hash" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "saads" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "ovitrampas" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(255) NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "neighborhood" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "saad_id" INT NOT NULL REFERENCES "saads" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cycles" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "start" DATE NOT NULL,
    "end" DATE,
    "number" INT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "ovitrampa_id" INT NOT NULL REFERENCES "ovitrampas" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cycleimages" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "eggs" INT NOT NULL  DEFAULT 0,
    "bad_eggs" INT NOT NULL  DEFAULT 0,
    "absolute_path" VARCHAR(255),
    "file_name" VARCHAR(255),
    "file_extension" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "cycle_id" INT NOT NULL REFERENCES "cycles" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users_scopes" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "scopes_id" INT NOT NULL REFERENCES "scopes" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
