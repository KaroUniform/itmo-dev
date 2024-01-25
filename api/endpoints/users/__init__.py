from datetime import MAXYEAR, MINYEAR, datetime
from api.endpoints.auth.FastAPI_users import fastapi_users
from fastapi import Depends, APIRouter
from api.db_model import User, UserRead, UserUpdate
from fastapi_limiter.depends import RateLimiter
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select
from api.db_model import User, TransactionHistory, get_session, MLModel
from api.endpoints.auth.FastAPI_users import current_active_user
from api.endpoints.predict.utils import validate_model_name
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from worker.data_models.elderly_people import DataModel

router = APIRouter()


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, seconds=5))],
)
async def users_get_history_of_transaction(
    start_date: datetime = datetime(MINYEAR, 1, 1),
    end_date: datetime = datetime(MAXYEAR, 12, 31),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(TransactionHistory)
        .filter(TransactionHistory.user_id == user.id)
        .filter(TransactionHistory.timestamp >= start_date)
        .filter(TransactionHistory.timestamp <= end_date)
        .order_by(TransactionHistory.timestamp.asc())
    )
    result = await session.execute(query)

    transactions = result.scalars().all()

    return [transaction.__dict__ for transaction in transactions]


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
