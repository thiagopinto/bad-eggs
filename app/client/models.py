from app.config import get_settings
from uuid import uuid4
from passlib.context import CryptContext
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

settings = get_settings()
client_secret_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Clients(Model):
    id = fields.IntField(pk=True)
    client_id = fields.UUIDField(default=uuid4)
    name = fields.CharField(max_length=255)
    responsible_name = fields.CharField(max_length=255)
    responsible_email = fields.CharField(max_length=255)
    client_secret_hash = fields.CharField(null=True, max_length=255)
    verified_hash = fields.CharField(null=True, max_length=255)
    verified_is = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["client_secret_hash"]

    @staticmethod
    def get_client_secret_hash(client_secret: str) -> str:
        return client_secret_context.hash(client_secret)

    @staticmethod
    def verify_client_secret(client_secret: str, client_secret_hash: str) -> bool:
        return client_secret_context.verify(client_secret, client_secret_hash)


ClientsOut = pydantic_model_creator(Clients, name="ClientsOut")
ClientsLight = pydantic_model_creator(
    Clients,
    name="ClientsIn",
    exclude=[
        "id",
        "client_id",
        "verified_hash",
        "verified_is",
        "created_at",
        "updated_at",
    ],
)


class ClientsIn(ClientsLight):
    client_secret: str
