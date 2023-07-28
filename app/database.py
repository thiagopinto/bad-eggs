from tortoise import Tortoise
from app.config import get_settings
import pkgutil
import app
import os

settings = get_settings()

# postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]
# postgresql+asyncpg://postgres:postgres@db:5432/foo
PROVIDER = settings.DATABASE_PROVIDER
USER = settings.DATABASE_USER
PASS = settings.DATABASE_PASS
HOST = settings.DATABASE_HOST
PORT =settings.DATABASE_PORT
NAME = settings.DATABASE_NAME
 
DATABASE_URL = f"{PROVIDER}{USER}:{PASS}@{HOST}:{PORT}/{NAME}"

models = []
aerich_models = ["aerich.models"]

for importer, modname, ispkg in pkgutil.iter_modules(app.__path__):
    if ispkg:
        if os.path.isfile(f"{importer.path}/{modname}/models.py"):
            __import__(f"app.{modname}.models")
            models.append(f"app.{modname}.models")
            aerich_models.append(f"app.{modname}.models")
async def init_db():

    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': models}
    )

    # Generate the schema
    #await Tortoise.generate_schemas()

print(DATABASE_URL)
print(models)

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": aerich_models,
            "default_connection": "default",
        },
    },
}