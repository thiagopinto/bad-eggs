from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from datetime import datetime
from app.models import Status
from app.auth.services import Protect, credentials_exception
from app.user.models import Users, UsersIn, UsersOut
from app.user.services import Mail
from app.config import get_settings
from typing import Annotated
from fastapi_pagination import Page
from fastapi_pagination.ext.tortoise import paginate

settings = get_settings()

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[UsersOut])
async def get_users(
    scopes: Annotated[str, Depends(Protect.check_token)],
):
    if "admin:list" not in scopes:
        raise credentials_exception

    return await paginate(Users.all().order_by("-updated_at"))


@router.get("/{user_id}", response_model=UsersOut)
async def get_user(
    scopes: Annotated[str, Depends(Protect.check_token)],
    user_id: int
):
    if "admin:show" not in scopes:
        raise credentials_exception

    try:
        return await Users.get(id=user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
        )


@router.post("/", response_model=UsersOut)
async def create_user(
    scopes: Annotated[str, Depends(Protect.check_token)],
    userIn: UsersIn,
    background_tasks: BackgroundTasks
):
    if "admin:create" not in scopes:
        raise credentials_exception

    user = await Users.filter(username=userIn.username).first()

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Users already exists"
        )

    user_dict = userIn.dict()
    user_dict["password_hash"] = Users.get_password_hash(user_dict["password"])
    user_dict.pop("password")
    user = await Users(**user_dict)
    await user.save()

    background_tasks.add_task(Mail.send_verify_email, user.id)

    return await UsersOut.from_tortoise_orm(user)


@router.put("/{user_id}", response_model=UsersOut)
async def update_user(
    scopes: Annotated[str, Depends(Protect.check_token)],
    user_id: int,
    userIn: UsersIn
):
    if "admin:update" not in scopes:
        raise credentials_exception

    try:
        user = await Users.get(id=user_id)
        user.name = userIn.name
        user.username = userIn.username
        if userIn.password is not None:
            user.password_hash = Users.get_password_hash(userIn.password)
        user.updated_at = datetime.now()
        await user.save()

        return await UsersOut.from_tortoise_orm(user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Users not found"
        )


@router.delete("/{user_id}", response_model=Status)
async def delete_user(
    scopes: Annotated[str, Depends(Protect.check_token)],
    user_id: int
):
    if "admin:delete" not in scopes:
        raise credentials_exception

    try:
        deleted_count = await Users.filter(id=user_id).delete()
        if not deleted_count:
            raise HTTPException(
                status_code=404, detail=f"Client {user_id} not found")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Users {user_id} not found"
        )
    return Status(message=f"Deleted user {user_id}")
