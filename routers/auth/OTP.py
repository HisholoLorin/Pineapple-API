from bson import ObjectId
from datetime import datetime, timedelta
import random
from routers.auth.Email import sendEmail


class OTP:
    def __init__(self):
        pass
    def generateOtp(self):
        return random.randint(1000, 9999)

    def saveOtp(self, userId, username, email, otp, type, db):
        cursor = db.otp.insert_one({
            "userId": ObjectId(userId),
            "otp": otp,
            "type": type,
            "createdAt": datetime.now(),
            "exp": datetime.now() + timedelta(minutes=5)
        })
        sendEmail(username=username, emailReciver=email, otp=otp)
        return str(cursor.inserted_id)

    def regenerateOtp(self, otpId, username, email, otp, type, db):
        cursor = db.otp.update_one({
            "_id": ObjectId(otpId)
        },
            { "$set": {
                "otp": otp,
                "type": type,
                "createdAt": datetime.now(),
                "exp": datetime.now() + timedelta(minutes=5)
            }
        }, upsert=True)
        sendEmail(username=username, emailReciver=email, otp=otp)

    def checkOtp(self, userName, otp):
        pass