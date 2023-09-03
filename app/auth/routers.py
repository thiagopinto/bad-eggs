from unittest import result
from fastapi import APIRouter, Form, HTTPException, status, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from app.auth.services import Auth
from app.client.models import Clients, ClientsOut
from app.user.models import Users, UsersOut
from app.client.services import Mail as ClientMail
from app.user.services import Mail as UserMail

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/client")
async def authorization_client(client_id: str = Form(), client_secret: str = Form()):
    return {"client_id": client_id, "client_secret": client_secret}


@router.post("/client/send/verify/token")
async def send_token_verify_client(
    client_id: str,
    responsible_email: str,
    background_tasks: BackgroundTasks,
):
    client = (
        await Clients.filter(client_id=client_id)
        .filter(responsible_email=responsible_email)
        .first()
    )

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clients {client_id} not found",
        )

    background_tasks.add_task(ClientMail.send_verify_email, client.id)
    return {"status": "send token"}


@router.get("/client/verify/{token}", response_model=ClientsOut)
async def verify_client(token: str):
    try:
        token_dict = ClientMail.verify_email(token)

        client = (
            await Clients.filter(client_id=token_dict["client_id"])
            .filter(verified_hash=token_dict["verified_hash"])
            .first()
        )

        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Clients {token_dict["client_id"]} not found',
            )

        client.verified_is = True
        client.updated_at = datetime.now()
        await client.save()

        return await ClientsOut.from_tortoise_orm(client)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/login", include_in_schema=False)
async def login(form_login: OAuth2PasswordRequestForm = Depends()):
    return form_login
    if form_login.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("Not send client_id"),
        )

    if form_login.client_secret is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("Not send client_secret"),
        )

    if form_login.username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("Not send username"),
        )

    if form_login.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str("Not send password"),
        )

    return await Auth.authenticate_by_client(
        form_login.client_id,
        form_login.client_secret,
        form_login.username,
        form_login.password,
    )


@router.post("/refresh")
async def refresh(refresh_token: str = Form()):
    return await Auth.refresh_token(refresh_token)


@router.post("/send/verify/token")
async def send_token_verify_user(
    username: str,
    background_tasks: BackgroundTasks,
):
    user = await Users.filter(username=username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Users {username} not found"
        )

    background_tasks.add_task(UserMail.send_verify_email, user.id)
    return {"status": "send token"}


@router.get("/verify/{token}", response_model=UsersOut)
async def verify_user(token: str):
    try:
        token_dict = UserMail.verify_email(token)

        user = (
            await Users.filter(id=token_dict["user_id"])
            .filter(verified_hash=token_dict["verified_hash"])
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Users {token_dict["user_id"]} not found',
            )

        user.verified_is = True
        user.updated_at = datetime.now()
        await user.save()

        return await UsersOut.from_tortoise_orm(user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
