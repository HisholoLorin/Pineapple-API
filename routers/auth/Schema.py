from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str


class OTP(BaseModel):
    otpId: str


class VerifyOTP(BaseModel):
    otpId: str
    otp: int


class ChangePassword(BaseModel):
    otpId: str
    password: str
    retypePassword: str
