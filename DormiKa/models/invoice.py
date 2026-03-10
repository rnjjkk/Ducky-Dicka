from datetime import datetime
from .enum import InvoiceStatus, InvoiceType

# ================== Invoice
class Invoice:
    __running_number = 1

    def __init__(self, type, room_id, amount, status=InvoiceStatus.UNPAID):
        self.__id = f"INV-{Invoice.__running_number:04d}"
        Invoice.__running_number += 1
        self.__type = type
        self.__room_id = room_id
        self.__amount = amount
        self.__status = status
        self.__date_create = datetime.now()

    @property
    def ID(self):
        return self.__id

    @property
    def amount(self):
        return self.__amount

    def PAID(self):
        self.__status = InvoiceStatus.PAID