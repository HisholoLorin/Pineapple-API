from fastapi import APIRouter, status, Depends, HTTPException
from core.database import getDb
from .Schema import SensorData
from .services import saveSensorData

router = APIRouter(
    prefix="/sensor",
    tags=["Sensor"],
    responses={404: {"description": "Not found"}}
)


@router.post("/data", status_code=status.HTTP_200_OK)
async def sensorData(data: SensorData, db=Depends(getDb)):
    await saveSensorData(data=data, db=db)
    return {"message": "Sensor Data is save in the database"}