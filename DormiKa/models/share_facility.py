from .enum import *
from .facility_booking import *
from .invoice import *
class ShareFacility:
    ID = 1
    def __init__(self):
        self.__id = f"SHARE-{ShareFacility.ID:04d}"
        self.__status = ShareFacilityStatus.AVAILABLE
        self.__facility_log = []
        ShareFacility.ID += 1
    # getter attribute ShareFacility
    @property
    def id(self):
        return self.__id
    
    @property
    def status(self):
        return self.__status
    
    @property
    def facility_log(self):
        return self.__facility_log
    
    def create_booking(self, resident_id, facility_id, building_id, booking_time):
        booking = BookingShareFacility(resident_id, facility_id, building_id, booking_time)
        return booking
    
    def create_booking(self, resident_id, facility_id, building_id, booking_time):
        booking = BookingShareFacility(resident_id, facility_id, building_id, booking_time)
        return booking

    def create_share_facility_invoice(self, resident_id, booking):
        return Invoice(InvoiceType.SHARE_FACILITY, booking.id, self.cost, InvoiceStatus.UNPAID)
    
class WashingMachine(ShareFacility):
    def __init__(self):
        super().__init__()
        self.__cost = 50
    
    # getter attribute WashingMachine
    @property
    def cost(self):
        return self.__cost

class MeetingRoom(ShareFacility):
    def __init__(self):
        super().__init__()
        self.__cost = 100

    # getter attribute MeetingRoom
    @property
    def cost(self):
        return self.__cost

