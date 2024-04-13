from pymongo import MongoClient
from typing import Generator
from core.config import getSetting

settings = getSetting()


def getDb():
    client = MongoClient(settings.MONGODB_URL)
    db = client.pineapple
    return db