from enum import Enum

class InvoiceStatus(Enum):
    ISSUED = "ISSUED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    DISPUTED = "DISPUTED"
    VOID = "VOID"

class Invoice:
    ID = 1
    
    def __init__(self, id, type, room_id, amount, status):
        self.__id = f"INV-{Invoice.ID:04d}"
        self.__type = type
        self.__room_id = room_id
        self.__amount = amount
        self.__status = status

        Invoice.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def amount(self):
        return self.__amount