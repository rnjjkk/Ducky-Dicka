import datetime
from .enum import ContractStatus, InvoiceType, InvoiceStatus
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
        self.__invoice_id = None

        Contract.ID += 1

    @property
    def id(self) -> str:
        return self.__id

    @property
    def resident(self):
        return self.__resident

    @property
    def status(self) -> ContractStatus:
        return self.__status

    @status.setter
    def status(self, new_status: ContractStatus):
        self.__status = new_status

    @property
    def invoice_id(self):
        return self.__invoice_id

    @invoice_id.setter
    def invoice_id(self, inv_id: str):
        self.__invoice_id = inv_id

    @property
    def room(self):
        return self.__room

    @room.setter
    def room(self, room):
        self.__room = room

    def validate_contract_status_for_handover(self):
        valid_statuses = [ContractStatus.ACTIVE, ContractStatus.PENDING_SIGN]
        if self.__status not in valid_statuses:
            raise ValueError(
                f"Contract {self.__id} cannot be handed over "
                f"(current status: {self.__status.value} — must be ACTIVE or PENDING_SIGN)"
            )

    def validate_for_signing(self):
        if self.__status != ContractStatus.DRAFT:
            raise ValueError(
                f"Contract {self.__id} cannot be signed "
                f"(current status: {self.__status.value} — must be DRAFT)"
            )

    def calculate_upgrade_amount(self, target_room_cost, moveDate):
        move_date = datetime.datetime.strptime(moveDate, "%Y-%m-%d").date()
        days_in_month = calendar.monthrange(move_date.year, move_date.month)[1]

        days_left = days_in_month - move_date.day + 1
        avg_new_room_cost = target_room_cost / days_in_month
        new_room_cost = avg_new_room_cost * days_left
        
        old_room_cost = (self.__room.monthly_rent / days_in_month) * days_left
        cost_diff = new_room_cost - old_room_cost

        return Invoice(InvoiceType.CONTRACT, round(cost_diff, 2), InvoiceStatus.UNPAID, self.__room.id)
