from typing import Any

import pandas as pd
from worker.models import AbstractMLModel, update_timer
from worker.data_models.elderly_people import DataModel


class LogisticRegression(AbstractMLModel):
    def train(self):
        raise NotImplementedError()

    def evaluate(self):
        raise NotImplementedError()

    def get_model_info(self):
        raise NotImplementedError()

    def set_hyperparameters(self):
        raise NotImplementedError()

    def get_hyperparameters(self):
        raise NotImplementedError()

    @update_timer  # This is importain!
    def predict(self, data: dict[str, Any]):
        validated_data = DataModel(**data)
        dataframe = pd.DataFrame(
            [validated_data.model_dump()],
            columns=[
                "temperature",
                "humidity",
                "CO2CosIRValue",
                "CO2MG811Value",
                "MOX1",
                "MOX2",
                "COValue",
                "hour",
            ],
        )
        return self.model.predict(dataframe)
