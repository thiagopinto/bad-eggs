from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.config import get_settings
from app.auth.routers import router as auth_router
from app.client.routers import router as client_router
from app.user.routers import router as user_router
from app.ovitrampa.routers import router as ovitrampa_router
from app.ovitrampa.saad.routers import router as saad_router

settings = get_settings()

router = APIRouter(redirect_slashes=True)
#prefix=settings.API_PREFIX
@router.get('/')
async def root(request: Request):
    # return RedirectResponse("/docs")
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

router.include_router(auth_router)
router.include_router(client_router)
router.include_router(user_router)
router.include_router(ovitrampa_router)
router.include_router(saad_router) 
