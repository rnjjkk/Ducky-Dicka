from enum import Enum
import datetime

from .invoice import Invoice


class ContractStatus(Enum):
    DRAFT = "DRAFT"
    PENDING_SIGN = "PENDING_SIGN"
    ACTIVE = "ACTIVE"
    ENDING_SOON = "ENDING_SOON"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"


class Contract:
    ID = 1

    def __init__(self, status: ContractStatus = ContractStatus.DRAFT):
        self.__id = Contract.ID
        self.__date_create = datetime.datetime.now()
        self.__room: object = None
        self.__cancel_rent_condition: str = None
        self.__move_in_date = None
        self.__status: ContractStatus = status
        self.__rental_time = None
        self.__monthly_rent = None

        Contract.ID += 1

    @property
    def id(self) -> str:
        """Return a stable contract identifier."""
        return f"LC-{self.__date_create.year}-{self.__id:04d}"

    @property
    def status(self) -> ContractStatus:
        return self.__status

    @property
    def room(self):
        return self.__room

    @room.setter
    def room(self, room):
        self.__room = room

    def calculate_upgrade_amount(self, target_room_rental: float, moveDate: str):
        """Calculate the pro-rated amount due when upgrading to a different room.
        """

        move_date = datetime.datetime.strptime(moveDate, "%Y-%m-%d").date()
        days_in_month = (datetime.date(move_date.year, move_date.month, 1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        days_in_month = days_in_month.day

        days_left = days_in_month - move_date.day + 1
        avg_new_room_cost = target_room_rental / days_in_month
        new_room_cost = avg_new_room_cost * days_left

        old_room_rental = getattr(self.__room, "rental", 0)
        old_room_cost = (old_room_rental / days_in_month) * days_left
        cost_diff = new_room_cost - old_room_cost

        return Invoice(
            id=None,
            type="UPGRADE",
            room_id=getattr(self.__room, "id", None),
            amount=round(cost_diff, 2),
            status="ISSUED",
        )
