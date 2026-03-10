from enum import Enum
from datetime import datetime, timedelta
from .enum import RoomStatus, RoomPrice, RoomType

class Room:
    ID = 1
    
    def __init__(
        self,
        building: object,
        floor: int,
        room_type: RoomType = RoomType.StandardRoom,
        basic_amenities: list | None = None,
        status: RoomStatus = RoomStatus.Available,
        rental: int = RoomPrice.StandardRoom,
    ):
        self.__room_id = f"RM-{Room.ID:04d}"
        self.__building = building
        self.__floor = floor
        self.__type = room_type
        self.__basic_amenities = basic_amenities or []
        self.__status = status
        self.__room_log: list = []
        self.__maintenance_tickets: list = []
        self.__monthly_rent = self.define_monthly_rent(room_type)
        self.__hold_expiry = None  # used when a room is temporarily reserved/held
				
				Room.ID += 1

    def define_monthly_rent(self, room_type):
        for type in RoomType:
            if room_type == type:
                return RoomPrice[type.name].value

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
    def monthly_rent(self):
        return self.__monthly_rent
        
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
