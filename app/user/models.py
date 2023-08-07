from app.config import get_settings
from passlib.context import CryptContext
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

settings = get_settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Origins(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    users: fields.ReverseRelation["Users"]

class Users(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    username = fields.CharField(max_length=255)
    verified_hash = fields.CharField(null=True, max_length=255)
    verified_is = fields.BooleanField(default=False)
    password_hash = fields.CharField(null=True, max_length=255)
    scopes: fields.ManyToManyRelation["Scopes"] = fields.ManyToManyField(
        "models.Scopes", related_name="users", through="users_scopes"
    )
    origin: fields.ForeignKeyRelation[Origins] = fields.ForeignKeyField(
        "models.Origins", related_name="users"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["password_hash"]

    @staticmethod
    def get_password_hash(password: str) -> str:
        return password_context.hash(password)

    @staticmethod
    def verify_password(password: str, client_secret_hash: str) -> bool:
        return password_context.verify(password, client_secret_hash)

    def dict(self):
        return {"id": self.id, "name": self.name, "username": self.username}


class Scopes(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255)
    users: fields.ManyToManyRelation[Users]
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def dict(self):
        return {"name": self.name}


UsersOut = pydantic_model_creator(Users, name="UsersOut")
UsersLight = pydantic_model_creator(
    Users,
    exclude=[
        "id",
        "verified_hash",
        "verified_is",
        "created_at",
        "updated_at",
    ],
)


class UsersIn(UsersLight):
    password: str


ScopesOut = pydantic_model_creator(Scopes, name="ScopesOut")
ScopesIn = pydantic_model_creator(
    Scopes,
    name="ScopesIn",
    exclude=[
        "id",
        "created_at",
        "updated_at",
    ],
)
