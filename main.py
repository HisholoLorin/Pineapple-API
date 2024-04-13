# from fastapi import FastAPI
# from routers import Sensor, User, WaterContainer
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
#
# app = FastAPI()
#
# app.include_router(Sensor.router)
# app.include_router(User.router)
# app.include_router(WaterContainer.router)
#
#
# uvicorn.run(app, host="10.14.73.26", port=5000)

from fastapi import FastAPI
from routers.auth import Auth
from routers.users import User
from routers.sensor import Sensor
import uvicorn
from starlette.middleware.authentication import AuthenticationMiddleware
from core.security import JWTAuth

app = FastAPI()

app.include_router(Auth.router)

app.include_router(User.router)
app.include_router(User.userRouter)

app.include_router(Sensor.router)

@app.get("/")
def welcomeMessage():
    return {"message": "Welcome to my pineapple web app"}

# Add Middleware
app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

# uvicorn.run(app, host="172.27.224.1", port=3000, reload=True, workers=2)
# uvicorn main:app --host 10.14.72.147 --port 3000