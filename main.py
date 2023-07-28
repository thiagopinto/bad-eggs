from app import get_application
from tortoise.contrib.fastapi import register_tortoise
from fastapi.staticfiles import StaticFiles
from app.database import DATABASE_URL, models
from fastapi_pagination import add_pagination

#import app.logging  # noqa: F401

app = get_application()
""" 
@app.on_event("startup")
def on_startup():
    init_db()
 """
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": models},
    generate_schemas=False,
    add_exception_handlers=True,
)
add_pagination(app)