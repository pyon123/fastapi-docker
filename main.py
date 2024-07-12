import os

from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv

from dto import execute
from dto.execute import TaskType

load_dotenv()

app = FastAPI()

@app.get("/")
def health_check():
    return {"Hello": "World"}

@app.post("/execute", response_model=execute.ResponseDTO)
async def execute_code(request: execute.RequestDTO):
    if request.task_type == TaskType.execute_code:
        return execute.ResponseDTO(result="result")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported task type: {request.task_type}")
    
port = int(os.getenv("PORT") or 8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)