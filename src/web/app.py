from fastapi import FastAPI

from src.core.config import settings
from src.web.user_route import router as user_router

app = FastAPI(debug=True)

PREFIX = f"/api/{settings.API_VERSION}"
app.include_router(user_router, tags=["users"], prefix=PREFIX)
