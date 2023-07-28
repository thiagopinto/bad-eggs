from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cycleimages" DROP COLUMN "absolute_path";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cycleimages" ADD "absolute_path" VARCHAR(255);"""
