from bson import ObjectId
from fastapi.exceptions import HTTPException
from starlette import status
from datetime import timedelta

from .Schema import TokenResponse, AccessTokenResponse
from .OTP import OTP
from routers.Serializer import UserSerializer
from core.security import createAccessToken, createRefreshToken
from core.config import getSetting

settings = getSetting()


def verifyUserAccess(user, db):
    if not user.isActive:
        raise HTTPException(status_code=400, detail={"Your account is inactive. Please contact support"},
                            headers={"WWW-Authenticate": "Bearer"})
    if not user.isVerified:
        # Trigger use account verification email
        otpId = OTP().saveOtp(
            userId=user.id,
            username=user.username,
            email=user.email,
            otp=OTP().generateOtp(),
            type="register",
            db=db)
        raise HTTPException(status_code=400, detail={
            "message": "Your account is not verified. We have send an email to your registered email, please verify your email.",
            "otpId": otpId
        },
        headers={"WWW-Authenticate": "Bearer"})


async def getUserToken(user, refreshToken=None):
    payload = {"id": user.id}
    accessTokenExpiresIn = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    accessToken = await createAccessToken(payload, accessTokenExpiresIn)

    if not refreshToken:
        refreshTokenExpireIn = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refreshToken = await createRefreshToken(payload, refreshTokenExpireIn)
        return TokenResponse(
            access_token=accessToken,
            refresh_token=refreshToken,
        )
    return AccessTokenResponse(
        access_token=accessToken,
    )


async def getUser(otpId=None, username=None, db=None):
    if not otpId and not username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid.")
    elif username:
        user = db.users.find_one({"$or": [{"username": username}, {"email": username}]}, {"username": 1, "email": 1})
    else:
        cursor = db.otp.find_one({"_id": ObjectId(otpId)})
        if not cursor:
            raise HTTPException(status_code=401, detail="Unauthorized.")
        user = db.users.find_one({"_id": cursor['userId']}, {"username": 1, "email": 1})
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    user = UserSerializer(user)
    return user
