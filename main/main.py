from fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel

from models.dorm import *
from models.employee import *
from models.staff import *
from models.resident import *

def create_resident_mock_data(count: int = 3):
    """Generate a list of mock Resident objects."""

    names = ["Kenny", "John", "Alice", "Mary", "Bob"]
    residents = []

    for i in range(min(count, len(names))):
        name = names[i]
        residents.append(
            Resident(
                name,
                18 + i,
                f"080000000{i}",
                status=AccountStatus.ACTIVE.value,
            )
        )

    return residents

def create_technician_mock_data():
    return [
        Technician(name="Tech A", phone_number="0800000001", compabilities=["PLUMBING"]),
        Technician(name="Tech B", phone_number="0800000002", compabilities=["ELECTRICAL"]),
        Technician(name="Tech C", phone_number="0800000003", compabilities=["AC"]),
    ]

def create_employee_mock_data():
    return [
        Employee("Alice"),
        Employee("Bob"),
    ]
    
dorm = Dorm("Ducka")

mock_residents = create_resident_mock_data(3)
for r in mock_residents:
    dorm.add_resident(r)

mock_employees = create_employee_mock_data()
for e in mock_employees:
    dorm.add_operation_staff(e)

mock_technicians = create_technician_mock_data()
for t in mock_technicians:
    dorm.add_technician(t)

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
    return dorm.request_maintenance(request.residentId, 
                                   request.roomId, 
                                   request.issueCategory)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",port=8000, log_level="info", reload=True)