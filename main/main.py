from models.dorm import Dorm
from fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

dorm = Dorm("Ducka")

app = FastAPI()

@app.post("/request-maintenance")
async def request_maintenance(resident_id, room_id, issue_category):
    res = dorm.request_maintenance(resident_id, room_id, issue_category)
    return res


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",port=8000, log_level="info", reload=True)