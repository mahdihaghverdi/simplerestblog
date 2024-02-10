from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    API_VERSION: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2 * 24 * 60  # two days
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def PREFIX(self):
        return f"/api/{self.API_VERSION}"


settings = Settings()
