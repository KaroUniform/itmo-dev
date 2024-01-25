import uuid
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy import select
from api.db_model import User, TransactionHistory, get_session, MLModel
from api.endpoints.auth.FastAPI_users import current_active_user
from api.endpoints.predict.utils import validate_model_name
from sqlalchemy.ext.asyncio import AsyncSession
from api.Asyncrq import asyncrq
from fastapi_limiter.depends import RateLimiter
from worker.data_models.elderly_people import DataModel
from arq.jobs import Job

router = APIRouter(
    dependencies=[Depends(RateLimiter(times=15, seconds=5))],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_models_list(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    results = await session.execute(select(MLModel))
    models = results.scalars().all()
    return [model.__dict__ for model in models]


@router.get(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
)
async def get_job_result(
    job_id: str,
    user: User = Depends(current_active_user),
):
    job = Job(job_id=job_id, redis=asyncrq.pool)
    res = await job.result(timeout=30)
    return res.tolist()[0]


@router.post(
    "/{model_name}",
    status_code=status.HTTP_201_CREATED,
    response_description="The task has been successfully created. Please track the execution by job_id",
)
async def get_predictions_for_data(
    data: DataModel,
    user: User = Depends(current_active_user),
    model_name: str = Depends(validate_model_name),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(MLModel).filter_by(model_name=model_name))
    model = result.scalar()
    if model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Model not found")

    if user.balance < model.model_cost:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient funds"
        )
    transaction = TransactionHistory(
        job_id=uuid.uuid4(),
        user_id=user.id,
        amount=-1 * model.model_cost,
        model_id=model.id,
    )
    session.add(transaction)
    await session.commit()
    job = await asyncrq.pool.enqueue_job(
        function="models_router",
        _job_id=str(transaction.job_id),
        model_name=model_name,
        data=data.model_dump(),
    )
    info = await job.info()
    return {
        "job_id": str(job.job_id),
        "job_try": str(info.job_try),
        "enqueue_time": str(info.enqueue_time),
        "remaining_balance": user.balance + transaction.amount,
        "amount_spent": transaction.amount,
    }
