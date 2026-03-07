from fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from models.dorm import Dorm
from models.resident import *

dorm = Dorm("Ducka")

res1 = Resident("kenny", 19, "1234567890", status="ACTIVE")

app = FastAPI()

class ChangeContractRequest(BaseModel):
    residentId: str
    currentLeaseContractId: str
    targetRoomId: str
    moveDate: str

"""
{
  "residentId": "1",
  "currentLeaseContractId": "1",
  "targetRoomId": "RM-STUDIO-A01-02-0001",
  "moveDate": "2026-2-27"
}
"""

@app.post("/change-contract")
async def change_lease_contract(request: ChangeContractRequest):
    return dorm.change_lease_contract(request.residentId,
                                      request.
                                      currentLeaseContractId,
                                      request.targetRoomId,
                                      request.moveDate
                                      )

class RequestMaintenance(BaseModel):
    residentId: str
    roomId: str
    issueCategory: str

"""
{
  "residentId": "1",
  "roomId": "1",
  "issueCategory": "PLUMBING"
}
"""

@app.post("/request-maintenance")
async def request_maintenance(request: RequestMaintenance):
    res = dorm.request_maintenance(request.residentId, 
                                   request.roomId, 
                                   request.issueCategory)
    return res


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",port=8000, log_level="info", reload=True)