from fastapi import APIRouter, status, Depends, Request, HTTPException
from typing import Union

from core.database import getDb
from core.security import oauth2Scheme
from .Schema import CreateUserRequest
from .services import createUserAccount, updateProfilePicture, getSensorData

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}}
)

userRouter = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2Scheme)]
)


@router.post('', status_code=status.HTTP_201_CREATED)
async def createUser(data: CreateUserRequest, db=Depends(getDb)):
    otpId = await createUserAccount(data=data, db=db)
    return {"message": "User account has been successfully created. Please verify you email", "otpId": otpId}


@userRouter.get('/me', status_code=status.HTTP_200_OK)
def getUsesDetail(request: Request):
    if request.user is False:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        return request.user


@userRouter.put('/update-picture', status_code=status.HTTP_202_ACCEPTED)
async def updatePicture(request: Request, image: Union[str, None] = None, db=Depends(getDb)):
    if request.user is False:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        return await updateProfilePicture(user=request.user, image=image, db=db)


@userRouter.get('/sensor-data', status_code=status.HTTP_200_OK)
async def sensorData(db=Depends(getDb)):
    return await getSensorData(db=db)
