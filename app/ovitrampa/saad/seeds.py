from app.ovitrampa.models import Saads
from app.config import get_settings


settings = get_settings()


async def run():
    saadsList = [
        {"name": "Norte"},
        {"name": "Sul"},
        {"name": "Leste"},
        {"name": "Sudeste"},
    ]

    for saad in saadsList:
        saadObject = Saads(**saad)
        await saadObject.save()

