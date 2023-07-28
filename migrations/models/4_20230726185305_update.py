from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cycles" DROP COLUMN "geometry";
        ALTER TABLE "ovitrampas" ADD "geometry" JSONB;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cycles" ADD "geometry" JSONB;
        ALTER TABLE "ovitrampas" DROP COLUMN "geometry";"""
