import datetime
from .enum import ContractStatus


class Contract:
    ID = 1

    def __init__(self, room, status=ContractStatus.DRAFT):
        self.__id = Contract.ID
        Contract.ID += 1
        self.__date_create = datetime.datetime.now()
        self.__room = room
        self.__cancel_rent_condition: str = None
        self.__move_in_date = None
        self.__status: ContractStatus = status
        self.__rental_time = None

    @property
    def room(self):
        return self.__room
    
