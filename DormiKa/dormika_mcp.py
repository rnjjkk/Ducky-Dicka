from fastmcp import FastMCP
from pydantic import BaseModel, Field

from models.dorm import Dorm
from models.employee import Employee
from models.staff import Cleaner, Technician, PlumbingTech, ElectricalTech, ACTech
from models.resident import Resident
from models.room import Room
from models.contract import Contract
from models.building import Building
from models.enum import (
    RoomType, RoomStatus, ContractStatus, AccountStatus,
    IssueCategory,
)
from models.maintenance_ticket import MaintenanceTicket
from models.invoice import Invoice

# ==================== Mock Data ====================

def create_resident_mock_data(count: int = 3):
    names = ["Kenny", "John", "Alice", "Mary", "Bob"]
    residents = []
    for i in range(min(count, len(names))):
        resident = Resident(
            names[i],
            f"080000000{i}",
            status=AccountStatus.ACTIVE.value,
        )
        residents.append(resident)
    return residents

def create_technician_mock_data():
    return [
        PlumbingTech(name="Tech A", phone_number="0800000001", water_meter_tool="WM-001"),
        ElectricalTech(name="Tech B", phone_number="0800000002", certification_no="CERT-ELEC-001"),
        ACTech(name="Tech C", phone_number="0800000003", gas_level_refrigerant=100.0),
    ]

def create_employee_mock_data():
    return [Employee(name) for name in ["Alice", "Bob", "Charlie", "Diana", "Eve"]]

def create_room_mock_data(building):
    return [
        Room(building=building, floor=1, room_type=RoomType.STUDIO_ROOM,   status=RoomStatus.AVAILABLE, rental=6500),
        Room(building=building, floor=2, room_type=RoomType.STANDARD_ROOM, status=RoomStatus.AVAILABLE, rental=8200),
        Room(building=building, floor=3, room_type=RoomType.ONE_BED_ROOM,  status=RoomStatus.AVAILABLE, rental=10500),
    ]

def create_building_mock_data():
    building = Building(floor_count=5, zone="A")
    for room in create_room_mock_data(building):
        building.add_room(room)
    return building

def create_contract_mock_data(resident, room, status: ContractStatus = ContractStatus.ACTIVE):
    contract = Contract(resident, room, status=status)
    room.status = RoomStatus.OCCUPIED
    resident.add_contract(contract)
    return contract

# ==================== Global Dorm State ====================

dorm: Dorm = None

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

    for t in create_technician_mock_data():
        dorm.add_technician(t)

# ==================== FastMCP ====================

mcp = FastMCP("DormiKa")

init_mock_data()

# ==================== Tools ====================

@mcp.tool()
def reset() -> dict:
    """Reset all mock data back to the initial state."""
    init_mock_data()
    return {"message": "Mock data has been reset successfully"}


class ChangeContractRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")
    currentLeaseContractId: str = Field(..., description="Current lease contract ID, e.g. LC-0001")
    targetRoomId: str = Field(..., description="Target room ID to move into, e.g. RM-0003")
    moveDate: str = Field(..., description="Move-in date in YYYY-M-D format, e.g. 2026-2-27")

@mcp.tool()
def change_contract(request: ChangeContractRequest) -> dict:
    """Change a resident's lease contract to a different room.
    Calculates a prorated upgrade invoice for the move date and updates room statuses.
    """
    return dorm.change_contract(
        request.residentId,
        request.currentLeaseContractId,
        request.targetRoomId,
        request.moveDate,
    )


class RequestMaintenanceRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")
    roomId: str = Field(..., description="Room ID, e.g. RM-0001")
    issueCategory: IssueCategory = Field(..., description="Category of the issue: PLUMBING, ELECTRICAL, or AC")

@mcp.tool()
def request_maintenance(request: RequestMaintenanceRequest) -> dict:
    """Submit a maintenance request for a room.
    Assigns an available employee and technician, and creates a maintenance ticket.
    """
    return dorm.request_maintenance(
        request.residentId,
        request.roomId,
        request.issueCategory.value,
    )


class StartMaintenanceRequest(BaseModel):
    technicianId: str = Field(..., description="Technician ID, e.g. TC-0001")
    notes: str = Field(None, description="Optional notes, e.g. 'Pipe leaking under the sink'")

@mcp.tool()
def start_maintenance(request: StartMaintenanceRequest) -> dict:
    """Start work on an assigned maintenance ticket.
    The technician must already have a ticket assigned.
    """
    return dorm.start_maintenance_workflow(request.technicianId, request.notes)


class FinishMaintenanceRequest(BaseModel):
    technicianId: str = Field(..., description="Technician ID, e.g. TC-0001")

@mcp.tool()
def finish_maintenance(request: FinishMaintenanceRequest) -> dict:
    """Mark a maintenance ticket as resolved.
    Calculates the cost and generates an invoice for the resident.
    """
    return dorm.finish_maintenance_workflow(request.technicianId)


# ==================== Entrypoint ====================

if __name__ == "__main__":
    mcp.run()