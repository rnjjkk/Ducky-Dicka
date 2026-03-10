from datetime import datetime
from .enum import InvoiceStatus, InvoiceType

# ================== Invoice
class Invoice:
    ID = 1
    
    def __init__(self, id, type, room_id, amount, status):
        self.__id = f"INV-{Invoice.ID:04d}"
        self.__type = type
        self.__room_id = room_id
        self.__amount = amount
        self.__status = status
        self.__date_create = datetime.now()
        
        Invoice.ID += 1

    @property
    def ID(self):
        return self.__id

    @property
    def amount(self):
        return self.__amount

        Invoice.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def amount(self):
        return self.__amount
      
    def paid(self):
        self.__status = InvoiceStatus.PAID
