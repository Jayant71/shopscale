from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    app_name: str = "Shopscale"
    debug_mode: bool = False
    database_url: str = "sqlite+aiosqlite:///./shopscale.db"
    jwt_secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    token_expiry_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")


config = Config()
