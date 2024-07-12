import os

from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv

from dto import execute
from dto.execute import TaskType
from services.docker import DockerContainer

load_dotenv()

app = FastAPI()

@app.get("/")
def health_check():
    return {"Hello": "World"}

@app.post("/execute", response_model=execute.ResponseDTO)
async def execute_code(request: execute.RequestDTO):
    if request.task_type == TaskType.execute_code:
        container = DockerContainer(request.resources, request.code)
        try:
            result = await container.execute()
            print(result)
            return execute.ResponseDTO(result=result)
        
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

        except RuntimeError as e:
            print(f"Execution error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported task type: {request.task_type}")
    
port = int(os.getenv("PORT") or 8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)