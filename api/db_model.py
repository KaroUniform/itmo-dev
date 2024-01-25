import asyncio
from datetime import timedelta
from typing import Any, AsyncGenerator
import uuid
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    String,
    UUID,
    DateTime,
    Float,
    ForeignKey,
    event,
    select,
    Enum,
    update,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.dialects.postgresql import JSON
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users import schemas
import enum


Base = declarative_base()

# Асинхронный URL для PostgreSQL
DATABASE_URL = "postgresql+asyncpg://people_safety:people_safety@postgres/people_safety"

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_size=2,
)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class TransactionStatusEnum(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    balance = Column(Float, default=0)

    __table_args__ = (
        CheckConstraint(
            "balance >= 0", name="check_positive_balance"
        ),  # Проверка, что balance больше 0
    )


class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    job_id = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    amount = Column(Integer)
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=True)
    result = Column(JSON, nullable=True)
    status = Column(
        Enum(TransactionStatusEnum), default=TransactionStatusEnum.IN_PROGRESS
    )
    err_reason = Column(String(512), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(64), unique=True)
    model_cost = Column(Float)


class UserRead(schemas.BaseUser[uuid.UUID]):
    balance: float


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


@event.listens_for(TransactionHistory, "after_insert")
def receive_after_insert(mapper, connection, target):
    async def async_receive_after_insert():
        async for session in get_session():
            user = await session.execute(select(User).filter(User.id == target.user_id))
            user = user.scalar_one_or_none()
            if user:
                user.balance += target.amount
                await session.commit()

    asyncio.get_event_loop().create_task(async_receive_after_insert())


@event.listens_for(TransactionHistory, "before_update")
def receive_after_update(mapper, connection, target):
    async def async_receive_after_update():
        async for session in get_session():
            if target.status == TransactionStatusEnum.FAILURE:
                # Выбираем пользователей, связанных с текущей транзакцией
                user = await session.execute(
                    select(User).where(User.id == target.user_id)
                )
                user = user.scalar_one_or_none()

                # Проверяем, изменился ли статус на Failure

                # Возвращаем средства
                user.balance += abs(target.amount)
                await session.execute(
                    update(TransactionHistory)
                    .where(TransactionHistory.job_id == target.job_id)
                    .values(amount=0)
                )

                await session.commit()

    asyncio.get_event_loop().create_task(async_receive_after_update())


@event.listens_for(User, "after_insert")
def on_insert_user(mapper, connection, target):
    new_transaction = TransactionHistory(
        job_id=uuid.uuid4(),
        user_id=target.id,
        amount=100,
        status=TransactionStatusEnum.SUCCESS,
        result={"message": "Trial credit of 100"},
    )

    async def add_transaction(new_transaction):
        async for session in get_session():
            session.add(new_transaction)
            await session.commit()

    asyncio.get_event_loop().create_task(add_transaction(new_transaction))


async def create_db_and_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def add_default_values():
    async for session in get_session():
        models_to_add = [
            MLModel(model_name="forest_model", model_cost=5),
            MLModel(model_name="lgb_model", model_cost=8),
            MLModel(model_name="log_reg_model", model_cost=3),
        ]

        for model in models_to_add:
            existing_model = (
                await session.execute(
                    select(MLModel).where(MLModel.model_name == model.model_name)
                )
            ).scalar()

            if not existing_model:
                session.add(model)

        await session.commit()


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
