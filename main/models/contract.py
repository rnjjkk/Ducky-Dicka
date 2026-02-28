from enum import Enum
import datetime

class ContractStatus(Enum):
    DRAFT = "DRAFT"
    PENDING_SIGN = "PENDING_SIGN"
    ACTIVE = "ACTIVE"
    ENDING_SOON = "ENDING_SOON"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"

class Contract:
    ID = 1

    def __init__(self, status=ContractStatus.DRAFT):
        self.__id = Contract.ID
        self.__date_create = datetime.datetime.now()
        self.__room: object = None
        self.__cancel_rent_condition: str = None
        self.__move_in_date = None
        self.__status: ContractStatus = status
        self.__rental_time = None
        self.__monthly_rent = None