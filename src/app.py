from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import (
    DuplicateUsernameError,
    UnAuthorizedError,
    ResourceNotFoundError,
)
from src.web.auth import router as auth_router
from src.web.drafts import router as draft_router
from src.web.users import router as user_router

app = FastAPI(debug=True)

app.include_router(user_router, tags=["users"], prefix=settings.PREFIX)
app.include_router(auth_router, tags=["auth"], prefix=settings.PREFIX)
app.include_router(draft_router, tags=["drafts"], prefix=settings.PREFIX)


@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_exception_handler(_, exc: DuplicateUsernameError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.__str__()},
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(_, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(UnAuthorizedError)
async def unauthorized_exception_handle(_, exc: UnAuthorizedError):
    status_code = status.HTTP_401_UNAUTHORIZED
    header = {"WWW-Authenticate": "Bearer"}
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
        headers=header,
    )
