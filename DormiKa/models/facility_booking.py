from .enum import *
class BookingShareFacility:
    ID = 1
    def __init__(self,facility):
        self.__id = f"BOOKING-{BookingShareFacility.ID:04d}"
        self.__facility = facility
        self.__status = BookingShareFacilityStatus.BOOKED
        self.__cost = facility.cost
        BookingShareFacility.ID += 1

    # getter attribute BookingShareFacility
    @property
    def id(self):
        return self.__id

    @property
    def facility(self):
        return self.__facility

    @property
    def status(self):
        return self.__status