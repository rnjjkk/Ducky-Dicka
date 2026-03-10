from datetime import datetime
from .enum import InvoiceStatus, InvoiceType

# ================== Invoice
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

    def PAID(self):
        self.__status = InvoiceStatus.PAID
