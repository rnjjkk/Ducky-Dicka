from .enum import *

class BookingShareFacility:
    ID = 1
    def __init__(self, resident_id, facility_id, building_id, booking_time):
        self.__id = f"BOOKING-{BookingShareFacility.ID:04d}"
        self.__resident_id = resident_id
        self.__facility_id = facility_id
        self.__building_id = building_id
        self.__booking_time = booking_time
        self.__status = BookingShareFacilityStatus.BOOKED
        BookingShareFacility.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def facility_id(self):
        return self.__facility_id

    @property
    def booking_time(self):
        return self.__booking_time

    @property
    def status(self):
        return self.__status

    def check_booking_time(self, facility_id, booking_time):
        return self.__facility_id == facility_id and self.__booking_time == booking_time
