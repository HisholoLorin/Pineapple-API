from fastapi import APIRouter, status, HTTPException
from .components.Firebase import Connect
from .components import Schema
from .components.checkToken import checkToken
from routers.sensor.ML.Pineapple import Pineapple

# class WaterContainer(BaseModel):
#     userName : str
#     token : str
#     height : float
#     capacity : float


router = APIRouter(
    prefix="/WaterContainer",
    tags=["Water Container"]
)

@router.post("/setData")
async def setData(waterContainer : Schema.WaterContainer):
    try:
        #Connection to firebase (real time database)
        firebase = Connect()
        DB = firebase.database()
        if checkToken(DB,waterContainer.userName,waterContainer.token):
            data = {'Height' : waterContainer.height, 'Capacity' : waterContainer.capacity}
            DB.child('Water Container').set(data)
            return {"detail" : {"Info" : {"Result" : "Success"}, "Status" : 1}}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Info":"Not Authorize", "Status" : 0})
    
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = {"detail" : {"Info" : "Something went wrong with the database"},"Status" : 0})

@router.post("/getData")
async def getData(tokenObject : Schema.Token):
    try:
        #Connection to firebase (real time database)
        firebase = Connect()
        DB = firebase.database()
        if checkToken(DB,tokenObject.userName,tokenObject.token):
            exist = DB.child("Water Container").get().val()
            if exist is not None:
                return {"detail" : {"Info" : {"Height" : exist['Height'], "Capacity" : exist['Capacity']}, "Status" : 1}}
            else:
                return {"detail" : {"Info" : {"Height" : 0, "Capacity" : 0},"Status" : 1}}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Info":"Not Authorize", "Status" : 0})
    
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = {"detail" : {"Info" : {"Result" : "Something went wrong with the database"},"Status" : 0}})
    
@router.post("/waterRequirement")
async def getsensorData(tokenObject : Schema.Token):
    try:
        #Connection to firebase (real time database)
        firebase = Connect()
        DB = firebase.database()
        if checkToken(DB,tokenObject.userName,tokenObject.token):
            exist = DB.child(Pineapple.currentYear()).child(Pineapple.currentMonthAndDay() + " Final").get().val()
            if exist is not None:
                soilMoisture = exist['SoilMoisture']
                if soilMoisture == 0:
                    waterRequirement = exist['WaterRequirement']
                    return {"detail" : {"Info" : {"WaterRequirement" : waterRequirement, "Status" : 1}}}
                else:
                    return  {"detail" : {"Info" : "Water is not required","Status" : 0}}      
            else:
                return {"detail" : {"Info" : "No data is Available","Status" : 0}}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"Info":"Not Authorize", "Status" : 0})
    
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = {"detail" : {"Info" : {"Result" : "Something went wrong with the database"},"Status" : 0}})