from bson import ObjectId
from fastapi.exceptions import HTTPException
from starlette import status
from datetime import datetime, timedelta

from core.security import verifyPassword, getRefreshTokenPayload, getPasswordHashed
from core.config import getSetting
from routers.Serializer import UserSerializer
from .OTP import OTP
from .helper import verifyUserAccess, getUserToken, getUser

settings = getSetting()


async def getToken(data, db):
    user = db.users.find_one({"$or": [{"username": data.username}, {"email": data.username}]}, {"image": 0})
    if not user:
        raise HTTPException(status_code=400, detail="Username is not registered with us",
                            headers={"WWW-Authenticate": "Bearer"})
    user = UserSerializer(user=user)
    if not verifyPassword(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid Password",
                            headers={"WWW-Authenticate": "Bearer"})
    verifyUserAccess(user=user, db=db)
    return await getUserToken(user=user)


async def getAccessToken(refreshToken, db):
    payload = getRefreshTokenPayload(refreshToken=refreshToken)

    exception = HTTPException(
        status_code=401,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"}
    )
    if payload is None:
        raise exception
    userId = payload.get('id', None)
    if not userId:
        raise exception

    user = db.users.find_one({"_id": ObjectId(userId)}, {"username": 1, "email": 1})
    user = UserSerializer(user)
    if not user:
        raise exception

    return await getUserToken(user=user, refreshToken=refreshToken)


async def regenerateOTP(data, type, db):
    otpId = data.otpId
    user = await getUser(otpId=otpId, db=db)
    OTP().regenerateOtp(
        otpId=otpId,
        username=user.username,
        email=user.email,
        type=type,
        otp=OTP().generateOtp(),
        db=db
    )


async def verifyOTP(data, type, db):
    otpId, otp = data.otpId, data.otp
    cursor = db.otp.find_one({"_id": ObjectId(otpId), "otp": otp})
    if not cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid OTP.")
    elif cursor["exp"] < datetime.now():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OTP expired.")

    if type == "register":
        user = db.users.find_one_and_update(
            {"_id": cursor["userId"]},
            {"$set":
                 {"isVerified": True,
                  "updatedAt": datetime.now()}}
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
        user = UserSerializer(user)
        return await getUserToken(user)
    else:
        cursor = db.otp.find_one_and_update(
            {"_id": ObjectId(otpId)},
            {"$set": {"isVerified": True,
                      "updatedAt": datetime.now(),
                      "exp": datetime.now() + timedelta(minutes=10)
                      }}
        )
        if not cursor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


async def forgotPassword(username, db):
    user = await getUser(username=username, db=db)
    otpId = OTP().saveOtp(
        userId=user.id,
        username=user.username,
        email=user.email,
        otp=OTP().generateOtp(),
        type="forget password",
        db=db)

    return otpId, user.email


async def changePassword(data, db):
    if data.password == data.retypePassword:
        cursor = db.otp.find_one({
            "_id": ObjectId(data.otpId),
            "isVerified": True,
            "exp": {"$gt": datetime.now()}
        })
        if not cursor:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Session Expired")
        db.users.update_one({"_id": cursor["userId"]}, {"$set": {"password": getPasswordHashed(data.password)}})
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Retype Password is incorrect.")
