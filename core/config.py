import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = os.environ.get("MONGODB_URL")

    # JWT
    JWT_SECRET: str = os.environ.get('JWT_SECRET')
    JWT_ALGORITHM: str = os.environ.get('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get('JWT_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.environ.get('JWT_TOKEN_EXPIRE_DAYS')

    # Email
    EMAIL_SENDER: str = os.environ.get("EMAIL_SENDER")
    EMAIL_PASSWORD: str = os.environ.get("EMAIL_PASSWORD")

    # Sensor
    SENSOR_ID: str = os.environ.get("SENSOR_ID")


def getSetting() -> Settings:
    return Settings()
