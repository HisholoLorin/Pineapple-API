import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = os.environ["MONGODB_URL"]

    # JWT
    JWT_SECRET: str = os.environ['JWT_SECRET']
    JWT_ALGORITHM: str = os.environ['JWT_ALGORITHM']
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ['JWT_TOKEN_EXPIRE_MINUTES']
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.environ['JWT_TOKEN_EXPIRE_DAYS']

    # Email
    EMAIL_SENDER: str = os.environ["EMAIL_SENDER"]
    EMAIL_PASSWORD: str = os.environ["EMAIL_PASSWORD"]

    # Sensor
    SENSOR_ID: str = os.environ["SENSOR_ID"]


def getSetting() -> Settings:
    return Settings()
