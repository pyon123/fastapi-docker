import os

from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def health_check():
    return {"Hello": "World"}

port = int(os.getenv("PORT") or 8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)