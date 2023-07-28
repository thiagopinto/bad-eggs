from app.client.models import Clients
from app.config import get_settings
settings = get_settings()


async def run():
    """
        client_id = Required(UUID, default=uuid4)
    client_secret_hash = Optional(str)
    name = Required(str)
    responsible_name = Required(str)
    responsible_email = Required(str)
    verified_hash = Optional(str)
    verified_is = Required(bool, default=False)


        client_dict = client.dict()
        client_dict["client_secret_hash"] = Clients.get_client_secret_hash(
            client_dict["client_secret"]
        )
        client_dict.pop("client_secret")
        client_obj = Clients(**client_dict)
        commit()
    """
    listClients = [
        {
            "client_secret": "secret",
            "name": "web",
            "responsible_name": "Thiago Pinto Dias",
            "responsible_email": "thiagopinto.lx@gmail.com",
        }
    ]

   
    for client in listClients:
        client["client_secret_hash"] = Clients.get_client_secret_hash(
            client["client_secret"]
        )
        client.pop("client_secret")
        clientObject =  Clients(**client)
        await clientObject.save()



