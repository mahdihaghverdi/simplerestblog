from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import Error
from src.core.utils import HTTP, APIKey
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


@app.exception_handler(Error)
async def handler_error_exception(_, exc: Error):
    code = exc.code
    code_message = exc.code_message
    message = exc.message

    _content = {"error": code_message}
    if message is not None:
        _content["details"] = message

    return JSONResponse(status_code=code, content=_content)


openapi_schema = get_openapi(title="SimpleRESTBlog", version="0.1.0", routes=app.routes)

openapi_schema["components"]["securitySchemes"] = {
    "HTTPBearer": HTTP(scheme="bearer", in_="header").dump(),
    "CookieAuth": APIKey(in_="cookie", name="access_token").dump(),
    "RefreshCookieAuth": APIKey(in_="cookie", name="refresh_token").dump(),
}

app.openapi_schema = openapi_schema
