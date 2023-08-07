from os import name
from app.user.models import Users, Scopes, Origins
from app.config import get_settings

settings = get_settings()


async def run():

    originList = [
        {"name": "Zoonoses"},
        {"name": "UFPI"}
    ]
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
            "origin_id": 1,
            "verified_is": True,
        },
    ]

    originObjectList = []
    scopeObjectList = []
    userObjectList = []

    for origin in originList:
        originObject = Origins(**origin)
        await originObject.save()
        originObjectList.append(originObject)

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

