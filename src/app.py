from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import DuplicateUsernameError, UnAuthorizedError
from src.web.auth import router as auth_router
from src.web.user_route import router as user_router

app = FastAPI(debug=True)

app.include_router(user_router, tags=["users"], prefix=settings.PREFIX)
app.include_router(auth_router, tags=["auth"], prefix=settings.PREFIX)


@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_exception_handler(_, exc: DuplicateUsernameError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.__str__()},
    )


@app.exception_handler(UnAuthorizedError)
async def unauthorized_exception_handle(*_):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
