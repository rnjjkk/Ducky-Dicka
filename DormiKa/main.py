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

class BookingRequest(BaseModel):
    resident_id: str
    room_id: str

@app.post("/request-booking")
async def request_booking(request: BookingRequest):
    resident = dorm.search_resident_by_id(request.resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")

    if resident.status == AccountStatus.SUSPEND.value:
        raise HTTPException(status_code=403, detail="Account restricted")

    current_hour = datetime.now().hour
    if not (8 <= current_hour <= 17):
        raise HTTPException(status_code=400, detail="Office hours not available")

    room = dorm.search_room_by_id(request.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    # auto-release holds if expired
    if hasattr(room, "is_hold_expired"):
        room.is_hold_expired()

    if room.status != RoomStatus.Available:
        raise HTTPException(status_code=400, detail="Room is busy or in maintenance")

    held = getattr(room, "hold", None)
    if held is None or not held(48):
        raise HTTPException(status_code=400, detail="Unable to reserve room")

    contract = Contract(status=ContractStatus.DRAFT)
    contract.room = room
    resident.add_contract(contract)

    return {
        "status": "success",
        "lease_id": contract.id,
        "room_id": room.id,
        "room_status": room.status.value if hasattr(room.status, 'value') else str(room.status),
        "message": "Booking successful, held for 48 hours."
    }

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