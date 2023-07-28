from app.config import get_settings
# from tortoise import Tortoise
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
import os

settings = get_settings()


class Saads(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    ovitrampas: fields.ReverseRelation["Ovitrampas"]
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["created_at", "updated_at"]


class Ovitrampas(Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=255)
    address = fields.CharField(max_length=255)
    neighborhood = fields.CharField(max_length=255)
    disabled = fields.BooleanField(default=False)
    saad: fields.ForeignKeyRelation[Saads] = fields.ForeignKeyField(
        "models.Saads", related_name="ovitrampas"
    )
    cycles: fields.ReverseRelation["Cycles"]
    geometry = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["created_at", "updated_at"]


class Cycles(Model):
    id = fields.IntField(pk=True)
    start = fields.DateField()
    end = fields.DateField(null=True)
    number = fields.IntField(null=True)
    ovitrampa: fields.ForeignKeyRelation[Ovitrampas] = fields.ForeignKeyField(
        "models.Ovitrampas", related_name="cycles"
    )
    images: fields.ReverseRelation["CycleImages"]
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["created_at", "updated_at"]


class CycleImages(Model):
    id = fields.IntField(pk=True)
    eggs = fields.IntField(default=0)
    bad_eggs = fields.IntField(default=0)
    file_name = fields.CharField(null=True, max_length=255)
    file_extension = fields.CharField(null=True, max_length=255)
    cycle: fields.ForeignKeyRelation[Cycles] = fields.ForeignKeyField(
        "models.Cycles", related_name="images"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def original(self) -> str:
        return f"/storage/original/{self.file_name}/{self.file_name}{self.file_extension}".strip()

    def thumbnail(self) -> str:
        return f"/storage/thumbnail/{self.file_name}/{self.file_name}{self.file_extension}".strip()
    
    def predictis(self) -> list[str]:
        try:
            storage_dir = os.path.join(os.getcwd(), "storage")
            predict_dir = os.path.join(storage_dir, "predict")
            path = os.path.join(predict_dir, self.file_name)
            files_names = os.listdir(path)
            files = []

            for file in files_names:
                files.append(
                    f"/storage/predict/{self.file_name}/{file}".strip())

            return files
        except:
            return []
    
    def processeds(self) -> list[str]:
        try:
            storage_dir = os.path.join(os.getcwd(), "storage")
            predict_dir = os.path.join(storage_dir, "processed")
            path = os.path.join(predict_dir, self.file_name)
            files_names = os.listdir(path)
            files = []

            for file in files_names:
                files.append(
                    f"/storage/processed/{self.file_name}/{file}".strip())

            return files
        except:
            return []

    class PydanticMeta:
        computed = ["original", "thumbnail", "predictis", "processeds"]
        exclude = ["created_at", "updated_at"]


class CycleImageSegmentations(Model):
    id = fields.IntField(pk=True)
    eggs = fields.IntField(default=0)
    bad_eggs = fields.IntField(default=0)
    imagem: fields.ForeignKeyRelation[CycleImages] = fields.ForeignKeyField(
        "models.CycleImages", related_name="segiments"
    )

# Tortoise.init_models(["app.ovitrampa.models"], "models")


SaadsOut = pydantic_model_creator(Saads, name="SaadsOut")

OvitrampasLight = pydantic_model_creator(
    Ovitrampas, name="OvitrampasLight", exclude=["id", "saad", "cycles"]
)


class OvitrampasIn(OvitrampasLight):
    saad_id: int


OvitrampasOut = pydantic_model_creator(Ovitrampas, name="OvitrampasOut")


class OvitrampasWithSaad(OvitrampasOut):
    saad_id: int
    saad: SaadsOut


CyclesLight = pydantic_model_creator(
    Cycles, name="CyclesLight", exclude=["id", "ovitrampa", "images"]
)


class CyclesIn(CyclesLight):
    ovitrampa_id: int


CyclesOut = pydantic_model_creator(Cycles, name="CyclesOut")


class CyclesWithOvitrampa(CyclesOut):
    ovitrampa_id: int
    ovitrampa: OvitrampasOut


CycleImagesLight = pydantic_model_creator(
    CycleImages, name="CycleImagesLight", exclude=["id", "cycle"]
)


class CycleImagesIn(CycleImagesLight):
    cycle_id: int


CycleImagesOut = pydantic_model_creator(CycleImages, name="CycleImagesOut")
