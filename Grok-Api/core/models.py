from pydantic import BaseModel
from typing import List

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "grok"

class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

class Models:
    @staticmethod
    def get_models() -> ModelList:
        models = [
            ModelInfo(id="grok-3-auto", object="model", created=0, owned_by="grok"),
            ModelInfo(id="grok-3-fast", object="model", created=0, owned_by="grok"),
            ModelInfo(id="grok-4", object="model", created=0, owned_by="grok"),
            ModelInfo(id="grok-4-mini-thinking-tahoe", object="model", created=0, owned_by="grok"),
        ]
        return ModelList(data=models)

    @staticmethod
    def get_model(model_id: str) -> ModelInfo:
        models = Models.get_models().data
        for model in models:
            if model.id == model_id:
                return model
        raise ValueError(f"Model {model_id} not found")