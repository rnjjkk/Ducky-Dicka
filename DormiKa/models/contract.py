import datetime
from .enum import ContractStatus
from .invoice import Invoice
import calendar

class Contract:
    ID = 1

    def __init__(self, resident, room, status: ContractStatus = ContractStatus.DRAFT):
        self.__id = f"LC-{Contract.ID:04d}"
        self.__date_create = datetime.datetime.now()
        self.__resident = resident
        self.__room = room
        self.__cancel_rent_condition: str = None
        self.__move_in_date = None
        self.__status: ContractStatus = status
        self.__rental_time = None
        self.__monthly_rent = None

        Contract.ID += 1

    @property
    def id(self) -> str:
        return self.__id

    @property
    def status(self) -> ContractStatus:
        return self.__status

    @property
    def room(self):
        return self.__room

    def calculate_upgrade_amount(self, target_room_cost, moveDate):
        move_date = datetime.datetime.strptime(moveDate, "%Y-%m-%d").date()
        days_in_month = calendar.monthrange(move_date.year, move_date.month)[1]

        days_left = days_in_month - move_date.day + 1
        print(days_left)
        avg_new_room_cost = target_room_cost / days_in_month
        print(avg_new_room_cost)
        new_room_cost = avg_new_room_cost * days_left
        print(new_room_cost)
        
        old_room_cost = (self.__room.ROOM_COST / days_in_month) * days_left
        print(old_room_cost)
        cost_diff = new_room_cost - old_room_cost

        return Invoice(round(cost_diff, 2))
