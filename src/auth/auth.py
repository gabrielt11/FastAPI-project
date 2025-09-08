from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from src.auth.manager import get_user_manager
from src.models import User
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET = os.getenv("SECRET")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User , int](
    get_user_manager,
    [auth_backend],
)


async def current_user(user: Optional[User ] = Depends(fastapi_users.current_user(optional=True))):
    return user
