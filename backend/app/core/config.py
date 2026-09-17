"""
Central application settings. All secrets/config come from environment variables
(.env locally) — nothing sensitive is hard-coded, per the SIH security requirements.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "UrbanSense AI"
    environment: str = "development"

    database_url: str = "sqlite:///./urbansense.db"

    jwt_secret_key: str = "CHANGE_ME_IN_ENV"  # overridden by .env in real use
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    demo_mode_default: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "URBANSENSE_"


settings = Settings()
