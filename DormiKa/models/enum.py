from enum import Enum

class ContractStatus(Enum):
    DRAFT = "DRAFT"
    PENDING_SIGN = "PENDING_SIGN"
    ACTIVE = "ACTIVE"
    ENDING_SOON = "ENDING_SOON"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"

class IssueCategory(str, Enum):
    PLUMBING = "PLUMBING"
    ELECTRICAL = "ELECTRICAL"
    AC = "AC"
    # add more as needed

class RoomType(Enum):
    StudioRoom = "StudioRoom"
    StandardRoom = "StandardRoom"
    OneBedRoomRoom = "OneBedRoomRoom"

class RoomPrice(Enum):
    StudioRoom = 6700
    StandardRoom = 9100
    OneBedRoomRoom = 10500

class RoomStatus(Enum):
    Available = "Available"
    Reserved = "Reserved"
    Occupied = "Occupied"
    Turnover_Cleaning = "Turnover_Cleaning"
    Maintenance = "Maintenance"
    Disable = "Disable"

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPEND = "SUSPEND"
    CLOSED = "CLOSED"

class InvoiceType(Enum):
    CONTRACT       = "invoice_contract"
    MAINTENANCE    = "invoice_maintenance"
    CLEANER        = "invoice_cleaner"
    CHAIR_FACILITY = "invoice_chair_facility"

class InvoiceStatus(Enum):
    PAID = "paid"
    UNPAID = "unpaid"

class AvailabilityStatus(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"

class MemberType(Enum):
    STANDARD = "STANDARD"
    PLUS = "PLUS"
    PLATINUM = "PLATINUM"

class MaintenanceStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"