import datetime
from .enum import ContractStatus
from .invoice import Invoice

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
    