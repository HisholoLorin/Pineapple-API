from bson import ObjectId
from fastapi.exceptions import HTTPException
from core.security import getPasswordHashed
from datetime import datetime
from routers.auth.OTP import OTP
from routers.Serializer import UserSerializer


async def createUserAccount(data, db):
    if db.users.find_one({"username": data.username}):
        raise HTTPException(status_code=422, detail=f"Username is already registered with us.")

    if db.users.find_one({"email": data.email}):
        raise HTTPException(status_code=422, detail=f"Email is already registered with us.")

    if data.password == data.retypePassword:
        newUser = {
            "username": data.username,
            "email": data.email,
            "password": getPasswordHashed(data.password),
            "isActive": True,
            "isVerified": False,
            "registeredAt": datetime.now(),
            "updatedAt": datetime.now(),
            "createdAt": datetime.now()
        }
    else:
        raise HTTPException(status_code=422, detail="Retype Password is incorrect.")
    user = db.users.insert_one(newUser)
    otpId = OTP().saveOtp(
        userId=str(user.inserted_id),
        username=data.username,
        email=data.email,
        otp=OTP().generateOtp(),
        type="register",
        db=db)
    return otpId


async def updateProfilePicture(user, image, db):
    user = UserSerializer(user)
    user = db.find_one_and_update({"_id": ObjectId(user.id)}, {"$set": {"image": image}})
    if not user:
        return {"message": "Something went wrong"}
    return user


async def getSensorData(db):
    morning = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    night = morning.replace(hour=23, minute=59, second=59, microsecond=0)

    sensorData = db.result.find_one({"createdAt": {"$gte": morning, "$lte": night}}, {"_id": 0})
    if not sensorData:
        return {"message": "No result were found"}
    return sensorData
