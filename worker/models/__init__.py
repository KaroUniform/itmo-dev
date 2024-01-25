from abc import ABC, abstractmethod
import asyncio
import logging
import pickle
import time
from typing import Callable


def update_timer(func) -> Callable:
    def wrapper(self, *args, **kwargs):
        self.last_predict_time = time.time()
        if self.model is None:
            self.load_model()
            self.logger.info(f"The model {self.name} has been loaded into memory")
        result = func(self, *args, **kwargs)
        return result

    return wrapper


class AbstractMLModel(ABC):
    model = None
    model_type = None
    file_path: str = r"worker/models/"
    last_predict_time: float = time.time()
    name: str

    def __init__(
        self,
        name: str,
        # loop: AbstractEventLoop,
        unload_interval: float = 1800,
        model_type: str = "",
    ) -> None:
        self.logger = logging.getLogger(name)
        loop = asyncio.get_event_loop()
        self.async_task = loop.create_task(
            self.unload_model_periodically(unload_interval)
        )
        self.name = name
        self.logger.info(f"The model class {self.name} has been created")
        super().__init__()

    @abstractmethod
    def train(self, data, labels):
        pass

    @abstractmethod
    def evaluate(self, test_data, test_labels):
        pass

    @abstractmethod
    def get_model_info(self):
        pass

    @abstractmethod
    def set_hyperparameters(self, **kwargs):
        pass

    @abstractmethod
    def get_hyperparameters(self):
        pass

    @abstractmethod
    @update_timer  # This is importain!
    def predict(self, data):
        pass

    def save_model(self, model_name: str = ""):
        model_name = model_name or self.name
        with open(
            self.file_path + model_name + "/" + model_name + ".pkl", "wb"
        ) as file:
            pickle.dump(self.model, file)

    def load_model(self, model_name: str = ""):
        model_name = model_name or self.name
        with open(
            self.file_path + model_name + "/" + model_name + ".pkl", "rb"
        ) as file:
            self.model = pickle.load(file)

    def unload_model(self):
        self.model = None

    async def unload_model_periodically(
        self, unload_interval: float = 1800
    ):  # 1800 sec = 30 min
        while True:
            await asyncio.sleep(unload_interval)
            if time.time() - self.last_predict_time >= unload_interval:
                self.unload_model()
                self.logger.info(f"The model {self.name} has been unloaded from memory")
