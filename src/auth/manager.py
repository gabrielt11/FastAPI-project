from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from src.database import User, get_user_db


class UserManager(BaseUserManager[User, int]):
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    def parse_id(self, id_user: str) -> int:
        return int(id_user)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
