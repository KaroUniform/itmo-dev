import json
from typing import Dict, Any

from sqlalchemy import select
from worker.models.log_reg_model import LogisticRegression
from worker.models.forest_model import DecisionTree
from worker.models.lgb_model import LGB
from api.db_model import TransactionHistory, get_session, TransactionStatusEnum
from sqlalchemy.exc import NoResultFound

dict_router = {
    "log_reg_model": LogisticRegression("log_reg_model"),
    "lgb_model": LGB("lgb_model"),
    "forest_model": DecisionTree("forest_model"),
}


async def models_router(
    ctx: Dict[str, Any],
    model_name: str,
    data: dict,
    **kwargs: Any,
):
    async for session in get_session():
        try:
            job_id = ctx.get("job_id", None)
            if not job_id:
                raise Exception("Something is wrong. job_id is None")

            transaction = await session.execute(
                select(TransactionHistory).filter_by(job_id=job_id)
            )
            transaction = transaction.scalar()

            fit_model = dict_router.get(model_name, None)
            if not fit_model:
                raise Exception("Model not found")
            result = fit_model.predict(data)
            if len(result) == 0:
                raise Exception(f"Something is wrong. Try again later: {result}")

            transaction.status = TransactionStatusEnum.SUCCESS

            json_data = json.dumps({"data": data, "result": result.tolist()})
            transaction.result = json_data
            await session.commit()

            return result

        except NoResultFound:
            print("NO ALLOWED TRANSACTION FOR JOB")
        except Exception as e:
            transaction.status = TransactionStatusEnum.FAILURE
            transaction.err_reason = str(e)
            await session.commit()
