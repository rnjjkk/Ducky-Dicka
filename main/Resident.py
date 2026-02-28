from datetime import datetime

class Resident:
    def __init__(self, name: str, age: str=None, phone_number: str=None, status: str="ACTIVE"):
        self.__id = None
        self.__name = name
        self.__age = age
        self.__phone_number = phone_number
        self.__strike = 0
        self.__date_create = datetime.now()
        self.__room_bookings = []
        self.__facility_bookings = []
        self.__contracts = []
        self.__discounts = []
        self.__inovices = []
        self.__receipts = []
        self.__status = status