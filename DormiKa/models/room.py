from enum import Enum
from datetime import datetime, timedelta


class RoomType(Enum):
    StudioRoom = "StudioRoom"
    StandardRoom = "StandardRoom"
    OneBedRoomRoom = "OneBedRoomRoom"


class RoomStatus(Enum):
    Available = "Available"
    Reserved = "Reserved"
    Occupied = "Occupied"
    Turnover_Cleaning = "Turnover_Cleaning"
    Maintenance = "Maintenance"
    Disable = "Disable"


class Room:
    def __init__(
        self,
        room_id: str,
        building: str,
        floor: int,
        room_type: RoomType = RoomType.StandardRoom,
        basic_amenities: list | None = None,
        status: RoomStatus = RoomStatus.Available,
        electric_cost: float = 0.0,
        water_cost: float = 0.0,
        rental: float = 0.0,
    ):
        self.__room_id = room_id
        self.__building = building
        self.__floor = floor
        self.__type = room_type
        self.__basic_amenities = basic_amenities or []
        self.__status = status
        self.__room_log: list = []
        self.__maintenance_tickets: list = []
        self.__electric_cost = electric_cost
        self.__water_cost = water_cost
        self.__rental = rental
        self.__hold_expiry = None  # used when a room is temporarily reserved/held


    @property
    def fid(self):
        return f"RM-{self.__building.id}-{self.__floor:02d}-{self.__room_id[-4:]}"

    @property
    def id(self):
        return self.__room_id

    @property
    def building(self):
        return self.__building

    @property
    def floor(self):
        return self.__floor

    @property
    def type(self):
        return self.__type

    @property
    def basic_amenities(self):
        return self.__basic_amenities

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    @property
    def room_log(self):
        return self.__room_log

    @property
    def maintenance_tickets(self):
        return self.__maintenance_tickets

    @property
    def electric_cost(self):
        return self.__electric_cost

    @property
    def water_cost(self):
        return self.__water_cost

    @property
    def rental(self):
        return self.__rental

    def add_maintenance_ticket(self, ticket):
        """Attach a maintenance ticket to this room."""
        self.__maintenance_tickets.append(ticket)

    def update_meter(self, meter_elect: float, meter_water: float):
        """Update meter readings and record the values in room log."""
        self.__electric_cost = meter_elect
        self.__water_cost = meter_water
        self.__room_log.append({
            "timestamp": datetime.now(),
            "electric_meter": meter_elect,
            "water_meter": meter_water,
        })
        return {"electric": meter_elect, "water": meter_water}

    def record_handover(self, meter_elect: float, meter_water: float):
        """Log handover meter readings in the room log."""
        self.__room_log.append({
            "timestamp": datetime.now(),
            "handover_electric": meter_elect,
            "handover_water": meter_water,
        })
        return {"handover_electric": meter_elect, "handover_water": meter_water}

    def hold(self, hours: int = 48) -> bool:
        """Temporarily reserve the room for a short time.

        This is used during a booking workflow before a contract is confirmed.
        """
        if self.__status != RoomStatus.Available:
            return False

        self.__status = RoomStatus.Reserved
        self.__hold_expiry = datetime.now() + timedelta(hours=hours)
        return True

    def is_hold_expired(self) -> bool:
        """Return True if the current hold has expired and reset status."""
        if self.__hold_expiry is None:
            return False

        if datetime.now() >= self.__hold_expiry:
            self.__hold_expiry = None
            self.__status = RoomStatus.Available
            return True

        return False
