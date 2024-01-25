import os
from fastapi import HTTPException, status

DIR_PATH = "worker/models/"


async def validate_model_name(model_name: str):
    directory_names = [
        d
        for d in os.listdir(DIR_PATH)
        if os.path.isdir(os.path.join(DIR_PATH, d)) and d.endswith("_model")
    ]

    if model_name not in directory_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid model name"
        )

    return model_name
