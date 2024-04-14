from bson import ObjectId
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from jose import jwt, JWTError
from starlette.authentication import AuthCredentials
from fastapi import Depends

from core.config import getSetting
from core.database import getDb
from routers.Serializer import UserSerializer

settings = getSetting()

pwdContext = CryptContext(schemes=['bcrypt'])
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def getPasswordHashed(password):
    return pwdContext.hash(password)


def verifyPassword(plainPassword, hashPassword):
    return pwdContext.verify(plainPassword, hashPassword)


async def createAccessToken(data, expiry: timedelta):
    payload = data.copy()
    expireIn = datetime.now() + expiry
    payload.update({"exp": expireIn})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def createRefreshToken(data, expiry: timedelta):
    payload = data.copy()
    expireIn = datetime.now() + expiry
    payload.update({"exp": expireIn})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def getRefreshTokenPayload(refreshToken):
    try:
        payload = jwt.decode(refreshToken, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    except JWTError:
        return None
    return payload


def getAccessTokenPayload(accessToken):
    try:
        payload = jwt.decode(accessToken, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
    except JWTError:
        return None
    return payload


def getCurrentUser(accessToken: str = Depends(oauth2Scheme), db=None):
    payload = getAccessTokenPayload(accessToken)
    if not payload or type(payload) is not dict:
        return None
    userId = payload.get('id', None)
    if not userId:
        return None
    if not db:
        db = getDb()
    user = db.users.find_one({"_id": ObjectId(userId)}, {"_id": 1, "username": 1, "email": 1, "image" : 1})
    user = UserSerializer(user)
    if not user:
        return {"message": f"something went wrong with userid {userId}"}
    return user


class JWTAuth:
    async def authenticate(self, conn):
        guest = (AuthCredentials('unauthenticated'), False)
        if 'Authorization' not in conn.headers:
            return guest
        accessToken = conn.headers.get('Authorization').split(' ')[1]  # Bearer token_hash
        if not accessToken:
            return guest
        user = getCurrentUser(accessToken=accessToken)
        if not user:
            return guest
        return AuthCredentials('authenticated'), user
