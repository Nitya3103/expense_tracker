from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    rates_api_url: str = "https://api.frankfurter.dev/v1"
    base_currency: str = "INR"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
