from pydantic import BaseModel, field_validator
from enum import Enum

class TaskType(Enum):
    execute_code = "execute_code"

class ResourceType(BaseModel):
    cpu: str
    gpu: str
    ram: str
    storage: str

    @field_validator('cpu', 'gpu')
    def validate_positive_int(cls, v: str) -> int:
        if not v.isdigit():
            raise ValueError(f'{v} should be a valid non-negative integer string.')
        return int(v)

    @field_validator('ram', 'storage')
    def validate_memory_format(cls, v: str) -> str:
        if not v[:-2].isdigit() or v[-2:].upper() not in ['MB', 'GB']:
            raise ValueError(f'{v} is not a valid format.')
        return v

class RequestDTO(BaseModel):
    task_type: TaskType
    code: str
    resources: ResourceType

class ResponseDTO(BaseModel):
    result: str
