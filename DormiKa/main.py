from fastapi import FastAPI, HTTPException, APIRouter
from contextlib import asynccontextmanager
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
from models.facility_booking import FacilityBooking

# ==================== Mock Data ====================

def create_resident_mock_data(count: int = 3):
    Resident.ID = 1

    names = ["Kenny", "John", "Alice", "Mary", "Bob"]
    residents = []

    for i in range(min(count, len(names))):
        name = names[i]
        resident = Resident(
            name,
            18 + i,
            f"080000000{i}",
        )
        print(f"Created Resident: {resident.id}")
        residents.append(resident)

    return residents

def create_technician_mock_data():
    technicians = [
        PlumbingTech(name="Tech A", phone_number="0800000001", water_meter_tool="WM-001"),
        ElectricalTech(name="Tech B", phone_number="0800000002", certification_no="CERT-ELEC-001"),
        ACTech(name="Tech C", phone_number="0800000003", gas_level_refrigerant=100.0),
    ]
    for t in technicians:
        print(f"Created Technician: {t.id} ({t.name}) caps={t.capabilities}")
    return technicians

def create_employee_mock_data():
    employees = [
        Employee("Alice"),
        Employee("Bob"),
        Employee("Charlie"),
        Employee("Diana"),
        Employee("Eve"),
    ]
    for e in employees:
        print(f"Created Employee: {e.fid} ({e.id})")
    return employees

def create_room_mock_data(building):
    rooms = [
        Room(building=building, floor=1, room_type=RoomType.STUDIO_ROOM,   status=RoomStatus.AVAILABLE, rental=6500),
        Room(building=building, floor=2, room_type=RoomType.STANDARD_ROOM, status=RoomStatus.AVAILABLE, rental=8200),
        Room(building=building, floor=3, room_type=RoomType.ONE_BED_ROOM,  status=RoomStatus.AVAILABLE, rental=10500),
    ]
    for r in rooms:
        print(f"Created Room: {r.id} ({r.type.value}) {r.status.value}")
    return rooms

def create_building_mock_data():
    building = Building(floor_count=5, zone="A")
    print(f"Created Building: {building.id}")
    rooms = create_room_mock_data(building)
    for room in rooms:
        building.add_room(room)
    return building

def create_contract_mock_data(resident, room, status: ContractStatus = ContractStatus.ACTIVE):
    contract = Contract(resident, room, status=status)
    room.status = RoomStatus.OCCUPIED
    resident.add_contract(contract)
    print(resident.contracts[0].id)
    print(room.id)
    return contract

# ==================== App Init ====================

dorm = None

def init_mock_data():
    global dorm

    Resident.ID = 1
    Technician.ID = 1
    Cleaner.ID = 1
    Employee.ID = 1
    Contract.ID = 1
    Building.ID = 1
    Room.ID = 1
    MaintenanceTicket.ID = 1
    Invoice._running_number = 1
    FacilityBooking.ID = 1

    dorm = Dorm("Ducka")

    mock_building = create_building_mock_data()
    dorm.add_building(mock_building)

    mock_residents = create_resident_mock_data(3)
    for r in mock_residents:
        dorm.add_resident(r)

    if mock_residents and mock_building.rooms:
        create_contract_mock_data(mock_residents[0], mock_building.rooms[0])

    mock_employees = create_employee_mock_data()
    for e in mock_employees:
        dorm.add_operation_staff(e)

    mock_technicians = create_technician_mock_data()
    for t in mock_technicians:
        dorm.add_technician(t)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mock_data()
    yield

app = FastAPI(lifespan=lifespan)

# ==================== Routers ====================

system_router      = APIRouter(prefix="",           tags=["System"])
contract_router    = APIRouter(prefix="/contract",  tags=["Contract"])
maintenance_router = APIRouter(prefix="/maintenance", tags=["Maintenance"])
cleaning_router    = APIRouter(prefix="/cleaning",  tags=["Cleaning"])
facility_router    = APIRouter(prefix="/facility",  tags=["Facility"])

# ==================== System ====================

@system_router.post("/reset")
async def reset_mock_data():
    init_mock_data()
    return {"message": "Mock data has been reset successfully"}

# ==================== Contract ====================

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

@contract_router.post("/change")
async def change_contract(request: ChangeContractRequest):
    return dorm.change_contract(
        request.residentId,
        request.currentLeaseContractId,
        request.targetRoomId,
        request.moveDate,
    )

# ==================== Maintenance ====================

class RequestMaintenanceBody(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    roomId: str = Field(..., example="RM-0001")
    issueCategory: IssueCategory = Field(..., example=IssueCategory.PLUMBING)

"""
{
  "residentId": "RS-0001",
  "roomId": "RM-0001",
  "issueCategory": "PLUMBING"
}
"""

@maintenance_router.post("/request")
async def request_maintenance(request: RequestMaintenanceBody):
    try:
        result = dorm.request_maintenance(request.residentId, request.roomId, request.issueCategory.value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

class StartMaintenanceBody(BaseModel):
    technicianId: str = Field(..., example="TC-0001")
    notes: str = Field(None, example="Pipe leaking under the sink")

"""
{
  "technicianId": "TC-0001",
  "notes": "Pipe leaking under the sink"
}
"""

@maintenance_router.post("/start")
async def start_maintenance(request: StartMaintenanceBody):
    try:
        result = dorm.start_maintenance_workflow(request.technicianId, request.notes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

class FinishMaintenanceBody(BaseModel):
    technicianId: str = Field(..., example="TC-0001")

"""
{
  "technicianId": "TC-0001"
}
"""

@maintenance_router.post("/finish")
async def finish_maintenance(request: FinishMaintenanceBody):
    try:
        result = dorm.finish_maintenance_workflow(request.technicianId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

# ==================== Cleaning ====================

class RequestCleaningRoomBody(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    roomId: str = Field(..., example="RM-0001")

"""
{
  "residentId": "RS-0001",
  "roomId": "RM-0001"
}
"""

@cleaning_router.post("/request")
async def request_cleaning_room(request: RequestCleaningRoomBody):
    try:
        result = dorm.request_cleaning_room(request.residentId, request.roomId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

# ==================== Facility Booking ====================

class BookShareFacilityRequest(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    buildingId: str = Field(..., example="A01")
    facilityId: str = Field(..., example="MR-001")
    bookingTime: str = Field(..., example="2026-03-15 14:00:00")
    facilityName: str = Field(default="Shared Facility", example="Meeting Room")

"""
{
  "residentId": "RS-0001",
  "buildingId": "A01",
  "facilityId": "MR-001",
  "bookingTime": "2026-03-15 14:00:00",
  "facilityName": "Meeting Room"
}
"""

@facility_router.post("/book")
async def book_share_facility(request: BookShareFacilityRequest):
    try:
        result = dorm.booking_share_facility(
            request.residentId,
            request.buildingId,
            request.facilityId,
            request.bookingTime,
            request.facilityName
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result

# ==================== Register Routers ====================

app.include_router(system_router)
app.include_router(contract_router)
app.include_router(maintenance_router)
app.include_router(cleaning_router)
app.include_router(facility_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
