from pydantic import BaseModel, Field
from enum import Enum

class TaskType(Enum):
    execute_code = "execute_code"

class ResourceType(BaseModel):
    cpu: str
    gpu: str
    ram: str
    storage: str

class RequestDTO(BaseModel):
    task_type: TaskType
    code: str
    resources: ResourceType

class ResponseDTO(BaseModel):
    result: str
