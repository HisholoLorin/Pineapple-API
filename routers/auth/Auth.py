from fastapi import APIRouter, status, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from core.database import getDb
from .services import getToken, getAccessToken, regenerateOTP, verifyOTP, forgotPassword, changePassword
from .Schema import OTP, VerifyOTP, ChangePassword

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}}
)


@router.post("/login", status_code=status.HTTP_200_OK)
async def authenticateUser(data: OAuth2PasswordRequestForm = Depends(), db=Depends(getDb)):
    return await getToken(data=data, db=db)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refreshAccessToken(refreshToken: str = Header(), db=Depends(getDb)):
    return await getAccessToken(refreshToken=refreshToken, db=db)


@router.post("/register/otp", status_code=status.HTTP_200_OK)
async def registerGenerateOTP(data: OTP, db=Depends(getDb)):
    await regenerateOTP(data=data, type="register", db=db)
    return {"message": "OTP Regenerated Successfully."}


@router.post("/register/otp-verify", status_code=status.HTTP_200_OK)
async def registerVerifyOTP(data: VerifyOTP, db=Depends(getDb)):
    return await verifyOTP(data=data, type="register", db=db)


# Forget Password
@router.post("/forgetpassword", status_code=status.HTTP_200_OK)
async def forgetPassword(username: str, db=Depends(getDb)):
    otpId, email = await forgotPassword(username=username, db=db)
    return {"message": f"OTP is sent to your email address : {email}", "otpId": otpId}


@router.post("/forgetpassword/otp", status_code=status.HTTP_200_OK)
async def forgetPasswordOTP(data: OTP, db=Depends(getDb)):
    await regenerateOTP(data=data, type="forget password", db=db)
    return {"message": "OTP Regenerated Successfully."}


@router.post("/forgetpassword/otp-verify", status_code=status.HTTP_200_OK)
async def forgetPasswordVerifyOTP(data: VerifyOTP, db=Depends(getDb)):
    await verifyOTP(data=data, type="forget password", db=db)
    return {"message": "OTP verified Successfully.", "otpId": data.otpId}


@router.post("/forgetpassword/changePassword", status_code=status.HTTP_200_OK)
async def changeUserPassword(data: ChangePassword, db=Depends(getDb)):
    await changePassword(data=data, db=db)
    return {"message": "Password Changed Successfully"}
