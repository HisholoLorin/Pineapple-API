from pydantic import BaseModel


class SensorData(BaseModel):
    sensorId: str
    temperature: float
    solarRadiation: float
    soilMoisture: int
    humidity: float
