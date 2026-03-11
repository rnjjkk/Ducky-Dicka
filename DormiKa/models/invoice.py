from datetime import datetime
from .enum import InvoiceStatus, InvoiceType

class Invoice:
    _running_number = 1

    def __init__(self, type, amount, status, room_id=None):
        self.__id = f"INV-{Invoice._running_number:04d}"
        self.__type = type
        self.__amount = amount
        self.__room_id = room_id
        self.__status = status
        self.__date_create = datetime.now()

        Invoice._running_number += 1

    @property
    def id(self):
        return self.__id

    @property
    def amount(self):
        return self.__amount

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: InvoiceStatus):
        self.__status = new_status

    @property
    def date_create(self):
        return self.__date_create

    def validate_for_payment(self):
        if self.__status == InvoiceStatus.PAID:
            raise ValueError(f"Invoice {self.__id} is already paid")

    def PAID(self):
        self.__status = InvoiceStatus.PAID