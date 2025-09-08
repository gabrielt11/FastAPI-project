from fastapi import FastAPI
from src.auth.schemas import UserCreate, UserRead
from src.auth.auth import auth_backend, fastapi_users
from src.links.router import router as links_router
import uvicorn

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(links_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info")
