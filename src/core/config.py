from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SRB_API_VERSION: str = "v1"
    SRB_DEBUG: bool = True
    SRB_PG_URL: str = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432"
    SRB_TEST_DATABASE_URL: str | None = None
    SRB_REDIS_CACHE_URL: str = "redis://@0.0.0.0:6379/0"
    SRB_SECRET_KEY: str
    SRB_ALGORITHM: str = "HS256"
    SRB_ACCESS_TOKEN_EXPIRE_MINUTES: int = 2 * 60  # two hours
    SRB_REFRESH_TOKEN_EXPIRE_MINUTES: int = 2 * 24 * 60  # two days
    SRB_TFA_EXPIRE_MINUTES: int = 15
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def PREFIX(self):
        return f"/api/{self.SRB_API_VERSION}"


settings = Settings()
