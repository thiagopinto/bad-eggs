from app.user.models import Users, Scopes
from app.config import get_settings

settings = get_settings()


async def run():
    scopeList = [
        {"name": "*", "description": "Permissions allowed to all resources"},
        {
            "name": "admin:all",
            "description": "Permissions allowed to administrations resources",
        },
        {
            "name": "admin:list",
            "description": "Permissions list to administrations resources",
        },
        {
            "name": "admin:create",
            "description": "Permissions create to administrations resources",
        },
        {
            "name": "admin:update",
            "description": "Permissions update to administrations resources",
        },
        {
            "name": "admin:show",
            "description": "Permissions show to administrations resources",
        },
        {
            "name": "admin:delete",
            "description": "Permissions delete to administrations resources",
        },
    ]

    password_hash = Users.get_password_hash("secret")

    userList = [
        {
            "name": "Thiago Pinto Dias",
            "username": "thiago@codebr.dev",
            "password_hash": password_hash,
            "verified_is": True,
        },
        {
            "name": "Pedro Pinto Dias",
            "username": "pedro@codebr.dev",
            "password_hash": password_hash,
            "verified_is": True,
        },
        {
            "name": "João Pinto Dias",
            "username": "joao@codebr.dev",
            "password_hash": password_hash,
            "verified_is": True,
        },
        {
            "name": "José Pinto Dias",
            "username": "jose@codebr.dev",
            "password_hash": password_hash,
            "verified_is": True,
        },
    ]

    scopeObjectList = []
    userObjectList = []
   
    for scope in scopeList:
        scopeObject = Scopes(**scope)
        await scopeObject.save()
        scopeObjectList.append(scopeObject)

    for user in userList:
        useObject = Users(**user)
        await useObject.save()
        userObjectList.append(useObject)

    for user in userObjectList:
        for scope in scopeObjectList:
            await user.scopes.add(scope)

        
