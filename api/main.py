from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aioredis
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from api.Asyncrq import asyncrq
from api.db_model import create_db_and_tables, add_default_values
from api.endpoints import auth, predict, users


app = FastAPI(title="elderly_people_safety")
app.include_router(auth.api_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(predict.router, prefix="/api/v1/models", tags=["predict"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


log = logging.getLogger("elderly_people_safety")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.on_event("startup")
async def startup_event():
    global redis
    redis = await aioredis.from_url(url="redis://redis")
    await FastAPILimiter.init(redis)
    await create_db_and_tables()
    await add_default_values()
    await asyncrq.create_pool()


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()
