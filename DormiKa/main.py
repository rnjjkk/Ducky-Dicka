from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from models.dorm import *
from models.employee import *
from models.staff import *
from models.resident import *
from models.room import *
from models.contract import *
from models.building import *
from models.enum import *

def create_resident_mock_data(count: int = 3):
    """Generate a list of mock Resident objects."""
    Resident.ID = 1  # Reset ID counter for consistent testing

    names = ["Kenny", "John", "Alice", "Mary", "Bob"]
    residents = []

    for i in range(min(count, len(names))):
        name = names[i]
        resident = Resident(
            name,
            18 + i,
            f"080000000{i}",
            status=AccountStatus.ACTIVE.value,
        )
        print(f"Created Resident: {resident.id}")
        residents.append(resident)

    return residents

def create_technician_mock_data():
    technicians = [
        Technician(name="Tech A", phone_number="0800000001", capabilities=["PLUMBING"]),
        Technician(name="Tech B", phone_number="0800000002", capabilities=["ELECTRICAL"]),
        Technician(name="Tech C", phone_number="0800000003", capabilities=["AC"]),
    ]
    for t in technicians:
        print(f"Created Technician: {t.id} ({t.name})")
    return technicians

def create_employee_mock_data():
    employees = [
        Employee("Alice"),
        Employee("Bob"),
    ]
    for e in employees:
        print(f"Created Employee: {e.fid} ({e.id})")
    return employees

def create_room_mock_data(building):
    rooms = [
        Room(
            building=building,
            floor=1,
            room_type=RoomType.StudioRoom,
            status=RoomStatus.Available,
            rental=6500,
        ),
        Room(
            building=building,
            floor=2,
            room_type=RoomType.StandardRoom,
            status=RoomStatus.Available,
            rental=8200,
        ),
        Room(
            building=building,
            floor=3,
            room_type=RoomType.OneBedRoomRoom,
            status=RoomStatus.Available,
            rental=10500,
        ),
    ]
    for r in rooms:
        print(f"Created Room: {r.id} ({r.type.value}) {r.status.value}")
    return rooms

def create_building_mock_data():
    # Building requires both floor and zone (used for building ID generation).
    # Zone is used as a prefix for building IDs; keep it consistent with room IDs.
    building = Building(floor_count=5, zone="A")
    print(f"Created Building: {building.id}")
    rooms = create_room_mock_data(building)
    for room in rooms:
        building.add_room(room)
    return building

def create_contract_mock_data(resident, room, status: ContractStatus = ContractStatus.ACTIVE):
    """Create a simple lease contract pointing to a room and attach it to a resident."""

    contract = Contract(resident.id, room.id, status=status)
    # Mark the room as occupied when it's under contract.
    room.status = RoomStatus.Occupied
    resident.add_contract(contract)
    
    print(resident.contracts[0].id)
    print(room.id)
    return contract

"""==============================================================================="""

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

    # Create a sample lease contract for the first resident using the first available room
    if mock_residents and mock_building.rooms:
        create_contract_mock_data(mock_residents[0], mock_building.rooms[0])

    mock_employees = create_employee_mock_data()
    for e in mock_employees:
        dorm.add_operation_staff(e)

    mock_technicians = create_technician_mock_data()
    for t in mock_technicians:
        dorm.add_technician(t)

class ChangeContractRequest(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    currentLeaseContractId: str = Field(..., example="LC-0001")
    targetRoomId: str = Field(..., example="RM-0003")
    moveDate: str = Field(..., example="2026-2-27")

"""
{
  "residentId": "RS-0001",
  "currentLeaseContractId": "LC-0001",
  "targetRoomId": "RM-0003",
  "moveDate": "2026-2-27"
}
"""

@app.post("/change-contract")
async def change_contract(request: ChangeContractRequest):
    return dorm.change_contract(
        request.residentId,
        request.currentLeaseContractId,
        request.targetRoomId,
        request.moveDate,
    )

"""
{
  "residentId": "RS-0001",
  "roomId": "RM-0002",
  "issueCategory": "PLUMBING"
}
{
  "residentId": "RS-0001",
  "roomId": "RM-0001",
  "issueCategory": "PLUMBING"
}
"""

class RequestMaintenance(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    roomId: str = Field(..., example="RM-0001")
    issueCategory: IssueCategory = Field(..., example=IssueCategory.PLUMBING)

@app.post("/request-maintenance")
async def request_maintenance(request: RequestMaintenance):
    try:
        result = dorm.request_maintenance(request.residentId, request.roomId, request.issueCategory.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",port=8000, log_level="info", reload=True)