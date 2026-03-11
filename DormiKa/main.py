from fastapi import FastAPI, HTTPException, APIRouter
from contextlib import asynccontextmanager
import uvicorn
from pydantic import BaseModel, Field
from typing import Optional

from models.dorm import *
from models.employee import *
from models.staff import *
from models.resident import *
from models.room import *
from models.contract import *
from models.building import *
from models.enum import *
from models.facility_booking import *

# ==================== Mock Data ====================

def create_resident_mock_data(count: int = 3):
    names  = ["Kenny", "John",  "Alice",  "Mary",  "Bob"]
    emails = ["kenny", "john",  "alice",  "mary",  "bob"]
    residents = []
    for i in range(min(count, len(names))):
        # BUG FIX: old code passed (name, 18+i, phone) — age was treated as email
        resident = Resident(
            name=names[i],
            email=f"{emails[i]}@example.com",
            phone_number=f"080000000{i}",
        )
        print(f"Created Resident: {resident.id}")
        residents.append(resident)
    return residents

def create_cleaner_mock_data():
    # BUG FIX: Cleaner auto-generates its own id via CL-{ID:04d},
    # do NOT pass id= as kwarg — it is ignored and creates confusion.
    cleaners = [
        Cleaner(name="Cleaner A", phone_number="0900000001"),
        Cleaner(name="Cleaner B", phone_number="0900000002"),
    ]
    for c in cleaners:
        print(f"Created Cleaner: {c.id} ({c.name})")
    return cleaners

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
    employees = [Employee(name) for name in ["Alice", "Bob", "Charlie", "Diana", "Eve"]]
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
    for room in create_room_mock_data(building):
        building.add_room(room)
    
    # Add share facilities
    from models.share_facility import MeetingRoom, WashingMachine
    meeting_rooms = [
        MeetingRoom(),
        MeetingRoom(),
    ]
    washing_machines = [
        WashingMachine(),
        WashingMachine(),
    ]
    for mr in meeting_rooms:
        building.add_meeting_room(mr)
        print(f"Created Meeting Room: {mr.id}")
    for wm in washing_machines:
        building.add_washing_machine(wm)
        print(f"Created Washing Machine: {wm.id}")
    
    return building

def create_contract_mock_data(resident, room, status: ContractStatus = ContractStatus.ACTIVE):
    contract = Contract(resident, room, status=status)
    room.status = RoomStatus.OCCUPIED
    resident.add_contract(contract)
    print(f"Created Contract: {contract.id} → Room {room.id}")
    return contract

# ==================== App Init ====================

dorm = None

def init_mock_data():
    global dorm

    # Reset all counters
    Resident.ID          = 1
    Technician.ID        = 1
    Cleaner.ID           = 1
    Employee.ID          = 1
    Contract.ID          = 1
    Building.ID          = 1
    Room.ID              = 1
    MaintenanceTicket.ID = 1
    Invoice._running_number  = 1
    BookingShareFacility.ID  = 1

    dorm = Dorm("Ducka")

    building = create_building_mock_data()
    dorm.add_building(building)

    residents = create_resident_mock_data(3)
    for r in residents:
        dorm.add_resident(r)

    if residents and building.rooms:
        create_contract_mock_data(residents[0], building.rooms[0])

    for e in create_employee_mock_data():
        dorm.add_operation_staff(e)

    for c in create_cleaner_mock_data():
        dorm.add_cleaner(c)

    for t in create_technician_mock_data():
        dorm.add_technician(t)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mock_data()
    yield

app = FastAPI(
    title="DormiKa API",
    description="Dormitory management system",
    lifespan=lifespan,
)

# ==================== Routers ====================

system_router      = APIRouter(prefix="",           tags=["System"])
resident_router    = APIRouter(prefix="/resident",    tags=["Resident"])
contract_router    = APIRouter(prefix="/contract",  tags=["Contract"])
maintenance_router = APIRouter(prefix="/maintenance", tags=["Maintenance"])
cleaning_router    = APIRouter(prefix="/cleaning",    tags=["Cleaning"])
member_router      = APIRouter(prefix="/member",      tags=["Member"])
payment_router     = APIRouter(prefix="/payment",     tags=["Payment"])
invoice_router     = APIRouter(prefix="/invoice",     tags=["Invoice"])
receipt_router     = APIRouter(prefix="/receipt",     tags=["Receipt"])
facility_router    = APIRouter(prefix="/facility",    tags=["Facility"])


# ==================================================
# SYSTEM
# ==================================================

@system_router.post("/reset")
async def reset_mock_data():
    """Reset all mock data to initial state."""
    init_mock_data()
    return {"message": "Mock data has been reset successfully"}


class SystemContractInvoiceBody(BaseModel):
    employeeId: str = Field(..., example="EM-0001")

@system_router.post("/system-contract-invoice")
async def system_contract_invoice(request: SystemContractInvoiceBody):
    """Generate monthly contract invoices for all active residents."""
    try:
        result = dorm.system_contract_invoice(request.employeeId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class AddStrikeBody(BaseModel):
    employeeId: str = Field(..., example="EM-0001")

@system_router.post("/add-strike")
async def add_strike(request: AddStrikeBody):
    """Add a strike to a resident's account."""
    try:
        result = dorm.add_strike(request.employeeId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# RESIDENT
# ==================================================

class SignInBody(BaseModel):
    name:        str = Field(..., example="Kenny")
    email:       str = Field(..., example="kenny@example.com")
    phoneNumber: str = Field(..., example="0812345678")

@resident_router.post("/sign-in")
async def sign_in(request: SignInBody):
    """Register a new resident account."""
    try:
        result = dorm.sign_in(request.name, request.email, request.phoneNumber)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": result}


# ==================================================
# CONTRACT
# ==================================================

class RequestBookingBody(BaseModel):
    residentId: str      = Field(..., example="RS-0001")
    buildingId: str      = Field(..., example="A01")
    roomType:   RoomType = Field(..., example=RoomType.STUDIO_ROOM)

@contract_router.post("/request")
async def request_booking(request: RequestBookingBody):
    """Request a room booking (holds the room for 48 h)."""
    try:
        result = dorm.request_booking(request.residentId, request.buildingId, request.roomType)
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return result


class SignContractBody(BaseModel):
    contractId: str = Field(..., example="LC-0001")

@contract_router.post("/sign")
async def sign_contract(request: SignContractBody):
    """Sign a draft contract (moves it to PENDING_SIGN)."""
    try:
        result = dorm.sign_contract(request.contractId)
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class HandoverBody(BaseModel):
    contractId: str   = Field(..., example="LC-0001")
    meterElect: float = Field(..., example=100.0)
    meterWater: float = Field(..., example=50.0)

@contract_router.post("/handover")
async def complete_handover(request: HandoverBody):
    """Record meter readings on room handover and activate the contract."""
    try:
        result = dorm.complete_handover(request.contractId, request.meterElect, request.meterWater)
    except (LookupError, KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class PayContractInvoiceBody(BaseModel):
    invoiceId: str = Field(..., example="INV-0001")

@contract_router.post("/pay")
async def pay_contract_invoice(request: PayContractInvoiceBody):
    """Pay a pending contract invoice directly."""
    try:
        result = dorm.pay_contract_invoice(request.invoiceId)
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class ChangeContractBody(BaseModel):
    residentId:            str = Field(..., example="RS-0001")
    currentLeaseContractId: str = Field(..., example="LC-0001")
    targetRoomId:          str = Field(..., example="RM-0003")
    moveDate:              str = Field(..., example="2026-03-15")

@contract_router.post("/change")
async def change_contract(request: ChangeContractBody):
    """Move a resident to a different room with a prorated upgrade invoice."""
    try:
        result = dorm.change_contract(
            request.residentId,
            request.currentLeaseContractId,
            request.targetRoomId,
            request.moveDate,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# MAINTENANCE
# ==================================================

class RequestMaintenanceBody(BaseModel):
    residentId:    str          = Field(..., example="RS-0001")
    roomId:        str          = Field(..., example="RM-0001")
    issueCategory: IssueCategory = Field(..., example=IssueCategory.PLUMBING)

@maintenance_router.post("/request")
async def request_maintenance(request: RequestMaintenanceBody):
    """Submit a maintenance request — assigns an employee and technician automatically."""
    try:
        result = dorm.request_maintenance(
            request.residentId, request.roomId, request.issueCategory.value
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class StartMaintenanceBody(BaseModel):
    technicianId: str            = Field(..., example="TC-0001")
    notes:        Optional[str]  = Field(None, example="Pipe leaking under the sink")

@maintenance_router.post("/start")
async def start_maintenance(request: StartMaintenanceBody):
    """Technician begins work on their assigned ticket."""
    try:
        result = dorm.start_maintenance_workflow(request.technicianId, request.notes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class FinishMaintenanceBody(BaseModel):
    technicianId: str = Field(..., example="TC-0001")

@maintenance_router.post("/finish")
async def finish_maintenance(request: FinishMaintenanceBody):
    """Technician marks the ticket resolved — generates an invoice for the resident."""
    try:
        result = dorm.finish_maintenance_workflow(request.technicianId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# CLEANING
# ==================================================

class RequestCleaningBody(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    roomId:     str = Field(..., example="RM-0001")

@cleaning_router.post("/request")
async def request_cleaning(request: RequestCleaningBody):
    """Submit a cleaning request for a room — assigns an available cleaner."""
    try:
        result = dorm.request_cleaning_room(request.residentId, request.roomId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class CleanRoomBody(BaseModel):
    cleanerId: str = Field(..., example="CL-0001")
    roomId: str = Field(..., example="RM-0001")

@cleaning_router.post("/start")
async def start_cleaning(request: CleanRoomBody):
    """Cleaner begins cleaning their assigned room."""
    try:
        # First assign the room to the cleaner, then start cleaning
        result = dorm.start_cleaning_workflow(request.cleanerId, request.roomId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class FinishCleaningBody(BaseModel):
    cleanerId: str = Field(..., example="CL-0001")
    roomId: str = Field(..., example="RM-0001")

@cleaning_router.post("/finish")
async def finish_cleaning(request: FinishCleaningBody):
    """Cleaner finishes the job — generates a cleaning invoice for the resident."""
    try:
        result = dorm.finish_cleaning_workflow(request.cleanerId, request.roomId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# MEMBER
# ==================================================

class CreateMemberBody(BaseModel):
    residentId: str = Field(..., example="RS-0001")
    memberType: str = Field(..., example="STANDARD")   # STANDARD | PLUS | PLATINUM

@member_router.post("/create")
async def create_member(request: CreateMemberBody):
    """Assign a membership tier to a resident and create a membership invoice."""
    try:
        result = dorm.create_member(request.residentId, request.memberType)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# PAYMENT
# ==================================================

class SelectPaymentBody(BaseModel):
    residentId:    str = Field(..., example="RS-0001")
    # BUG FIX: valid values are 'bank_account' or 'card' — not 'PROMPTPAY'
    paymentMethod: str = Field(..., example="bank_account")
    invoiceIds:    str = Field(..., example="INV-0001, INV-0002")

@payment_router.post("/select")
async def select_payment(request: SelectPaymentBody):
    """Choose a payment method and select invoices to pay."""
    try:
        result = dorm.select_payment_method_and_invoices(
            request.residentId, request.paymentMethod, request.invoiceIds
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


class PayBody(BaseModel):
    residentId:  str = Field(..., example="RS-0001")
    paymentData: str = Field(..., example="REF-ABC1234567")

@payment_router.post("/pay")
async def pay(request: PayBody):
    """Submit payment data to confirm and settle selected invoices."""
    try:
        result = dorm.payment_system(request.residentId, request.paymentData)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# INVOICE
# ==================================================

@invoice_router.get("/{resident_id}")
async def display_invoice(resident_id: str):
    """List all pending invoices for a resident."""
    try:
        result = dorm.display_invoice(resident_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# RECEIPT
# ==================================================

@receipt_router.get("/{resident_id}")
async def display_receipt(resident_id: str):
    """List all payment receipts for a resident."""
    try:
        result = dorm.display_receipt(resident_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================================================
# FACILITY
# ==================================================

class BookShareFacilityBody(BaseModel):
    residentId:  str = Field(..., example="RS-0001")
    buildingId:  str = Field(..., example="A01")
    facilityId:  str = Field(..., example="SHARE-0001")
    bookingTime: str = Field(..., example="2026-03-15 14:00:00")

@facility_router.post("/book")
async def book_share_facility(request: BookShareFacilityBody):
    """Book a shared facility (meeting room, washing machine, etc.). Creates an invoice automatically."""
    try:
        result = dorm.booking_share_facility(
            request.residentId,
            request.facilityId,
            request.buildingId,
            request.bookingTime,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ==================== Register Routers ====================

app.include_router(system_router)
app.include_router(resident_router)
app.include_router(contract_router)
app.include_router(maintenance_router)
app.include_router(cleaning_router)
app.include_router(member_router)
app.include_router(payment_router)
app.include_router(invoice_router)
app.include_router(receipt_router)
app.include_router(facility_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
