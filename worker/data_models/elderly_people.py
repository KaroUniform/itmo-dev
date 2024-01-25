from pydantic import BaseModel


class DataModel(BaseModel):
    temperature: float
    humidity: float
    CO2CosIRValue: float
    CO2MG811Value: float
    MOX1: float
    MOX2: float
    COValue: float
    hour: int
