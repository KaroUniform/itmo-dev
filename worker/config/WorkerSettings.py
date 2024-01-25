from api.config.ArqSettings import arqsettings
from worker.models_worker import models_router


class WorkerSettings:
    functions = [models_router]
    redis_settings = arqsettings
