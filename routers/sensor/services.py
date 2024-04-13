from fastapi import HTTPException, status
from datetime import datetime
import pandas as pd

from core.config import Settings
from .ML.Pineapple import calculateWaterRequirement


async def saveSensorData(data, db):
    if data.sensorId != Settings().SENSOR_ID:
        raise HTTPException(status_code=401, detail="Sensor ID mismatch")

    if boundaryValueAnalysis(data):
        morning = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        night = morning.replace(hour=23, minute=59, second=59, microsecond=0)

        db.sensor.update_one({"createdAt": {"$gte": morning, "$lte": night}}, {
            "$push": {
                "temperature": data.temperature,
                "solarRadiation": data.solarRadiation,
                "soilMoisture": data.soilMoisture,
                "humidity": data.humidity,
            },
            "$set": {
                "updatedAt": datetime.now(),
                "createdAt": datetime.now(),
            }
        }, upsert=True)
        calculateWaterRequirement(db=db)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Outliers detected")


class RoundValue:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, round(value, 2))


def boundaryValueAnalysis(data=None):
    df = pd.read_csv("routers/sensor/ML/Result.csv")
    df = df.describe().iloc[3:, :-2]
    IQR = df.iloc[3, :] - df.iloc[1, :]
    min = (df.iloc[1, :] - 1.5 * IQR).to_dict()
    max = (df.iloc[3, :] + 1.5 * IQR).to_dict()

    min = RoundValue(**min)
    max = RoundValue(**max)

    if data.temperature < min.min_temperature or data.temperature > max.max_temperature:
        # Trigger push notification
        return False
    elif data.solarRadiation < min.solar_radiation or data.solarRadiation > max.solar_radiation:
        # Trigger push notification
        return False
    elif data.humidity < min.relative_humidity or data.humidity > max.relative_humidity:
        # Trigger push notification
        return False
    else:
        return True
