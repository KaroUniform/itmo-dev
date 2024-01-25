from fastapi.responses import HTMLResponse
from api.endpoints.auth.FastAPI_users import (
    fastapi_users,
    auth_backend,
)
from fastapi import Depends, APIRouter, Request
from api.db_model import User, UserCreate, UserRead
from fastapi_limiter.depends import RateLimiter

api_router = APIRouter()

api_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    dependencies=[Depends(RateLimiter(times=5, seconds=5))],
)
api_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    dependencies=[Depends(RateLimiter(times=5, seconds=5))],
)


# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )
