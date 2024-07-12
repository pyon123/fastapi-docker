## Project Overview
This project is a Python Flask Backend designed to handle client-side requests for managing and executing tasks. It features dynamic allocation of resources and execution of code within Docker containers, tailored to the specific requirements of each task.

This project is for running the code snippet in an isolated environemnt and manage system resources dynamically.

Here's the [video](https://www.awesomescreenshot.com/video/29505770?key=04b6dd6c2c030da6f210423a29cda0ea)

## Pre-request
This project is tested on `Ubuntu` machine and the following guide is to explain how to install the environment on Ubuntu. 

### Docker and Docker engine
Need to install Docker and Docker engine first. Please check the installation guide [here](https://docs.docker.com/engine/install/ubuntu/).

### Python
Here are multiple ways to install python on ubuntu.
This project used `pyenv` and python `v3.12.1`.

### Nvidia
If you have gpu in your local machine and want to use gpu resource, then you need to install [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) before using it.


## Install Project and Run
### Installation
Run the following command to install necessary dependencies.
```
pip install -r requirements.txt
```

### Run project
Run in dev mode
```
fastapi dev main.py
```

Run in prod mode
```
python main.py
```

## Validation

### Client request example
Example 1:
```
{
    "task_type": "execute_code",
    "code": "print('Hello, World!')",
    "resources": {
        "cpu": "2",
        "gpu": "0",
        "ram": "512MB",
        "storage": "1GB"
    }
}
```
Example 2:
```
{
    "task_type": "execute_code",
    "code": "for i in range(5): print(f'Count {i}')",
    "resources": {
        "cpu": "1",
        "gpu": "0",
        "ram": "256MB",
        "storage": "500MB"
    }
}
```

### API request validation
Request Type:
```
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
```

Requests are validated automatically using Pydantic based on the defined data structures:
1. `task_type` should be one of the value in `TaskType` Enum
2. `cpu` and `gpu` should be a valid non-negative integer string. otherwise raise ValueError
3. `ram` and `storage` should be specific format like 500MB, 1GB, etc, otherwise raise ValueError 

### Resource validation
The project validates system resources (CPU, GPU, and memory) assuming only one container runs at the same time:

For checking available CPU and memory, `psutil` python lib is used. \
For GPU, `pynvml` is used.

### Timeout
Docker containers have a default timeout of 30 seconds for code execution. If the timeout expires, then stop runing and emit error message to client 

## Consideration

### Resource Check
Need to track the system resource and allocated resources by the existing running containers and validate available resources correctly before run docker container. especially cpu and memory.

This can be managed via a database or Docker API.

### GPU Allocation
Decide whether GPUs should be allocated to each container individually or shared across all Docker containers.

### Database usage
Would be good to use Database and track/record the task and the docker container status & the result in database level

### Performance optimization
Currently this project runs the docker container within sepcific timeout (default 30 seconds), but it would be ideal to run the service in background and notify the result via websocket or polling the status from client side for better client experience.

### Missing parts
- TDD
- Linting
