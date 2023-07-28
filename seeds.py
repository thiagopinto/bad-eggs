from app.database import init_db
from app.user.seeds import run as user_seeds
from app.ovitrampa.saad.seeds import run as saad_seeds
from app.client.seeds import run as client_seeds
import app.logging  # noqa: F401
import asyncio

async def init():
    await init_db()
    await user_seeds()
    await saad_seeds()
    await client_seeds()

asyncio.run(init())

