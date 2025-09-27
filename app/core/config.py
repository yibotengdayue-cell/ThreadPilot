from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "change_me"
    JWT_EXPIRE_MIN: int = 120
    LICENSE_DEMO_OK: int = 1  # 1=允许演示模式
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
