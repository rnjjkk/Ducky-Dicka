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
    STUDIO_ROOM = "StudioRoom"
    STANDARD_ROOM = "StandardRoom"
    ONE_BED_ROOM = "OneBedRoomRoom"


class RoomPrice(Enum):
    STUDIO_ROOM = 6700
    STANDARD_ROOM = 9100
    ONE_BED_ROOM = 10500


class RoomStatus(Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    OCCUPIED = "Occupied"
    TURNOVER_CLEANING = "Turnover_Cleaning"
    MAINTENANCE = "Maintenance"
    DISABLE = "Disable"


class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPEND = "SUSPEND"
    CLOSED = "CLOSED"


class InvoiceType(Enum):
    CONTRACT = "invoice_contract"
    MAINTENANCE = "invoice_maintenance"
    CLEANER = "invoice_cleaner"
    MEMBER = "invoice_member"
    SHARE_FACILITY = "invoice_share_facility"


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


class MemberPrice(Enum):
    STANDARD = 990
    PLUS = 2790
    PLATINUM = 9890


class CleaningStatus(Enum):
    REQUESTED = "Requested"
    CLEANING = "Cleaning"
    FINISHED = "Finished"


class BookingStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class ShareFacilityPrice(Enum):
    MeetingRoom = 100
    WashingMachine = 50


class ShareFacilityStatus(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class BookingShareFacilityStatus(Enum):
    BOOKED = "BOOKED"
    IN_USE = "IN_USE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MaintenanceStatus(Enum):
    REPORTED = "REPORTED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class MaintenanceCost(Enum):
    ELECTRICAL = 750
    PLUMBING = 1000
    AC = 500
