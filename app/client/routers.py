from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from datetime import datetime
from app.client.models import Clients, ClientsOut, ClientsIn
from app.client.services import Mail
from app.models import Status
from typing import Annotated
from app.auth.services import Protect, credentials_exception

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[ClientsOut])
async def get_clients(scopes: Annotated[str, Depends(Protect.check_token)]):
    if "admin:list" not in scopes:
        raise credentials_exception

    return await ClientsOut.from_queryset(Clients.all())


@router.get("/{client_id}", response_model=ClientsOut)
async def get_client(
    scopes: Annotated[str, Depends(Protect.check_token)], client_id: int
):
    if "admin:show" not in scopes:
        raise credentials_exception

    try:
        return await ClientsOut.from_queryset_single(Clients.get(id=client_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clients not found"
        )


@router.post("/", response_model=ClientsOut)
async def create_client(
    scopes: Annotated[str, Depends(Protect.check_token)],
    client: ClientsIn,
    background_tasks: BackgroundTasks,
):
    if "admin:create" not in scopes:
        raise credentials_exception

    client_dict = client.dict()
    client_dict["client_secret_hash"] = Clients.get_client_secret_hash(
        client_dict["client_secret"]
    )
    client_dict.pop("client_secret")
    try:
        client_obj = await Clients(**client_dict)
        await client_obj.save()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clients not create",
        )

    background_tasks.add_task(Mail.send_verify_email, client_obj.id)

    return await ClientsOut.from_tortoise_orm(client_obj)


@router.put("/{client_id}", response_model=ClientsOut)
async def update_client(
    scopes: Annotated[str, Depends(Protect.check_token)],
    client_id: int,
    clientIn: ClientsIn,
):
    if "admin:update" not in scopes:
        raise credentials_exception

    try:
        client = await Clients.get(id=client_id)
        client.name = clientIn.name
        client.responsible_name = clientIn.responsible_name
        client.responsible_email = clientIn.responsible_email

        if clientIn.client_secret is not None:
            client.client_secret_hash = Clients.get_client_secret_hash(
                clientIn.client_secret
            )
        client.updated_at = datetime.now()
        await client.save()
        return await ClientsOut.from_tortoise_orm(client)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Clients not found"
        )


@router.delete("/{client_id}", response_model=Status)
async def delete_client(
    scopes: Annotated[str, Depends(Protect.check_token)], client_id: int
):
    if "admin:update" not in scopes:
        raise credentials_exception

    try:
        deleted_count = await Clients.filter(id=client_id).delete()
        if not deleted_count:
            raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} not found",
        )
    return Status(message=f"Deleted client {client_id}")
