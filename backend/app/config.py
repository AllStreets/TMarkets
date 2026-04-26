from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_url: str
    redis_url: str
    openai_api_key: str = ""
    fred_api_key: str = ""
    alpha_vantage_key: str = ""
    polygon_api_key: str = ""
    news_api_key: str = ""
    gnews_api_key: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_to: str = ""

settings = Settings()
