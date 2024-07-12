from pydantic import BaseModel, field_validator
from enum import Enum
from services.docker import ResourceType

class TaskType(Enum):
    execute_code = "execute_code"

class RequestDTO(BaseModel):
    task_type: TaskType
    code: str
    resources: ResourceType

class ResponseDTO(BaseModel):
    result: str
