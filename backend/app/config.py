from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables"""

    # Database
    database_url: str = "postgresql://studyuser:studypass@localhost:5432/studyvault"

    # App
    app_name: str = "StudyVault API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "studyvaultv12345"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
