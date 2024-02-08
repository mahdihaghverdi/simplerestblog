from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import DuplicateUsernameError
from src.web.user_route import router as user_router

app = FastAPI(debug=True)

PREFIX = f"/api/{settings.API_VERSION}"
app.include_router(user_router, tags=["users"], prefix=PREFIX)


@app.exception_handler(DuplicateUsernameError)
async def duplicate_username_exception_handler(_, exc: DuplicateUsernameError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.__str__()},
    )
