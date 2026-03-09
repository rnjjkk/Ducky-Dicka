import datetime
# import sqlite3
from enum import Enum

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPEND = "SUSPEND"
    CLOSED = "CLOSED"

# conn = sqlite3.connect(r"C:\Users\James\Desktop\Ducky-Dicka\main\residents.db")
# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS residents (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     age INTEGER,
#     phone_number TEXT,
#     status TEXT
# )
# """)
# conn.commit()

class Resident:
    ID = 1
    
    def __init__(self, name: str, age: str=None, phone_number: str=None, status: str="ACTIVE"):
        self.__id = Resident.ID
        self.__name = name
        self.__age = age
        self.__phone_number = phone_number
        self.__strike = 0
        self.__date_create = datetime.datetime.now()
        self.__room_bookings = []
        self.__facility_bookings = []
        self.__contracts = []
        self.__discounts = []
        self.__invoices = []
        self.__receipts = []
        self.__status = status

        # cursor.execute(
        #     "INSERT INTO residents (name, age, phone_number, status) VALUES ( ?, ?, ?, ?)",
        #     (self.__name, self.__age, self.__phone_number, self.__status)
        # )
        # conn.commit()

        Resident.ID += 1

    @property
    def fid(self):
        return f"RS-{self.__date_create.year}-{self.__id:04d}"

    @property
    def id(self):
        return self.__id

    @property
    def status(self):
        return self.__status

    @property
    def contracts(self):
        return self.__contracts

    @property
    def invoices(self):
        return self.__invoices

    def add_contract(self, contract):
        self.__contracts.append(contract)

    def add_invoice(self, invoice):
        self.__invoices.append(invoice)

    def search_contract_by_id(self, contractId):
        for contract in self.__contracts:
            if int(contract.id[-4:]) == int(contractId):
                return contract
        return None