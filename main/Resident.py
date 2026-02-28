import datetime
import sqlite3

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
        self.id = Resident.ID
        self.__name = name
        self.__age = age
        self.__phone_number = phone_number
        self.__strike = 0
        self.__date_create = datetime.datetime.now()
        self.__room_bookings = []
        self.__facility_bookings = []
        self.__contracts = []
        self.__discounts = []
        self.__inovices = []
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
        return f"RS-{self.__date_create.year}-{self.id:04d}"


res1 = Resident("Ken", 25, "123456789", "ACTIVE")
print(res1.fid)   # e.g., 1

res2 = Resident("Alice", 30, "987654321", "ACTIVE")
print(res2.fid)   # e.g., 2