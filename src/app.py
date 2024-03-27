from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette import status
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import (
    DuplicateUsernameError,
    UnAuthorizedError,
    ResourceNotFoundError,
    DraftPublishedBeforeError,
    DatabaseError,
    ForbiddenException,
)
from src.web.auth import router as auth_router
from src.web.comments import router as comment_router
from src.web.drafts import router as draft_router
from src.web.globals import router as global_router
from src.web.posts import router as post_router
from src.web.users import router as user_router

app = FastAPI(debug=True)

app.include_router(user_router, tags=["users"], prefix=settings.PREFIX)
app.include_router(auth_router, tags=["auth"], prefix=settings.PREFIX)
app.include_router(draft_router, tags=["drafts"], prefix=settings.PREFIX)
app.include_router(post_router, tags=["posts"], prefix=settings.PREFIX)
app.include_router(global_router, tags=["global"])
app.include_router(comment_router, tags=["comments"], prefix=settings.PREFIX)


# TODO: improve the exception handlers
@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_exception_handler(_, exc: DuplicateUsernameError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.__str__()},
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_exception_handler(_, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
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


@app.exception_handler(DraftPublishedBeforeError)
async def draft_published_before(_, exc: DraftPublishedBeforeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(DatabaseError)
async def database_integrity_error(_, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )


@app.exception_handler(ForbiddenException)
async def database_error(_, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message},
    )


openapi_schema = get_openapi(title="SimpleRESTBlog", version="0.1.0", routes=app.routes)

openapi_schema["components"]["securitySchemes"] = {
    "HTTPBearer": {"type": "http", "scheme": "bearer", "in": "headers"},
    "CookieAuth": {"type": "apiKey", "in": "cookie", "name": "access_token"},
    "RefreshCookieAuth": {"type": "apiKey", "in": "cookie", "name": "refresh_token"},
}

app.openapi_schema = openapi_schema
