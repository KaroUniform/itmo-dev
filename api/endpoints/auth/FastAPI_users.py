import uuid
from typing import Any, Optional
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import RedisStrategy
import redis.asyncio
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend
from api.db_model import User
from fastapi_users.db import SQLAlchemyUserDatabase
from api.db_model import get_user_db

redis = redis.asyncio.from_url("redis://redis:6379", decode_responses=True)

cookie_transport = CookieTransport(
    cookie_name="people_safety",
    cookie_max_age=3600,
)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600 * 24)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = "TEST"
    verification_token_secret = "TEST"

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


current_active_user = fastapi_users.current_user(active=True)
