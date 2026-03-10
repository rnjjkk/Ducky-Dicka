from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from models.dorm import *
from models.employee import *
from models.staff import *
from models.resident import *
from models.room import Room, RoomType, RoomStatus
from models.contract import Contract, ContractStatus
from models.building import Building
from models.contract import Contract, ContractStatus

def create_resident_mock_data(count: int = 3):
    """Generate a list of mock Resident objects."""
    Resident.ID = 1  # Reset ID counter for consistent testing

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

def create_room_mock_data(building):
    return [
        Room(
            room_id="RM-STUDIO-A01-01-0001",
            building=building,
            floor=1,
            room_type=RoomType.StudioRoom,
            status=RoomStatus.Available,
            rental=6500,
        ),
        Room(
            room_id="RM-STANDARD-A01-02-0001",
            building=building,
            floor=2,
            room_type=RoomType.StandardRoom,
            status=RoomStatus.Available,
            rental=8200,
        ),
    ]

def create_building_mock_data():
    building = Building(floor="A01")
    rooms = create_room_mock_data(building)
    for room in rooms:
        building.add_room(room)
    return building

def create_contract_mock_data(resident, room, status: ContractStatus = ContractStatus.ACTIVE):
    """Create a simple lease contract pointing to a room and attach it to a resident."""

    contract = Contract(status=status)
    contract.room = room
    # Mark the room as occupied when it's under contract.
    room.status = RoomStatus.Occupied
    resident.add_contract(contract)
    
    print(resident.contracts[0].id, "================================================================")
    print(room.id)
    return contract

""""==============================================================================="""

dorm = None

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize in-memory mock data when the API starts."""
    global dorm
    dorm = Dorm("Ducka")

    # Mock room/building data (needed for room lookup during maintenance requests)
    mock_building = create_building_mock_data()
    dorm.add_building(mock_building)

    mock_residents = create_resident_mock_data(3)
    for r in mock_residents:
        dorm.add_resident(r)

    mock_employees = create_employee_mock_data()
    for e in mock_employees:
        dorm.add_operation_staff(e)

    mock_technicians = create_technician_mock_data()
    for t in mock_technicians:
        dorm.add_technician(t)

class ChangeContractRequest(BaseModel):
    residentId: str = Field(..., example="1")
    currentLeaseContractId: str = Field(..., example="1")
    targetRoomId: str = Field(..., example="RM-STUDIO-A01-01-0001")
    moveDate: str = Field(..., example="2026-2-27")

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
{
  "residentId": "1",
  "roomId": "RM-STUDIO-A01-01-0001",
  "issueCategory": "PLUMBING"
}
"""

class RequestMaintenance(BaseModel):
    residentId: str = Field(..., example="1")
    roomId: str = Field(..., example="RM-STUDIO-A01-01-0001")
    issueCategory: IssueCategory = Field(..., example=IssueCategory.PLUMBING)

@app.post("/request-maintenance")
async def request_maintenance(request: RequestMaintenance):
    return dorm.request_maintenance(request.residentId, 
                                   request.roomId, 
                                   request.issueCategory)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",port=8000, log_level="info", reload=True)