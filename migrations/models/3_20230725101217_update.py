from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "ovitrampas" ADD "disabled" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "ovitrampas" RENAME COLUMN "description" TO "description";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "ovitrampas" RENAME COLUMN "description" TO "description";
        ALTER TABLE "ovitrampas" DROP COLUMN "disabled";"""
