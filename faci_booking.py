from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, datetime
import uvicorn

# ==========================================
#               CLASS ZONE
# ==========================================

class FacilityStatus(Enum):
    Available = 1
    Reserved = 2
    In_Use = 3
    Maintenance = 4
    Disabled = 5

class AccountStatus(Enum):
    Applicant = 1
    Active = 2
    Suspended = 3
    Closed = 4

class User:
    def __init__(self, name, id, email, phone_number):
        self.__name = name
        self.__id = id
        self.__email = email
        self.__phone_number = phone_number

    @property
    def id(self):
        return self.__id

class Resident(User):
    def __init__(self, name, id, email, phone_number):
        super().__init__(name, id, email, phone_number)
        self.__move_in_date = date.today()
        self.__booking_share_facility_list = [] # List to store Booking objects
        self.__status = AccountStatus.Active.name

    def add_booking(self, booking):
        self.__booking_share_facility_list.append(booking)

class Share_Facility:
    def __init__(self, facility_id, status):
        self.__facility_id = facility_id
        self.__status = status

    @property
    def id(self):
        return self.__facility_id

class Meeting_Room(Share_Facility):
    def __init__(self, facility_id, status, size):
        super().__init__(facility_id, status)
        self.__size = size

class Building:
    def __init__(self, building_id, floor):
        self.__building_id = building_id
        self.__floor = floor
        self.__share_facility_list = []

    @property
    def id(self):
        return self.__building_id

    @property
    def share_facility_list(self):
        return self.__share_facility_list

    def add_facility(self, facility):
        self.__share_facility_list.append(facility)

class Booking_Share_Facility:
    def __init__(self, resident_id, building_id, share_facility_id, booking_time):
        self.__resident_id = resident_id
        self.__building_id = building_id
        self.__share_facility_id = share_facility_id
        self.__booking_time = booking_time

    @property
    def share_facility_id(self):
        return self.__share_facility_id
    
    @property
    def booking_time(self):
        return self.__booking_time

class Dorm:
    def __init__(self, name):
        self.__name = name
        self.__building_list = []
        self.__resident_list = []
        # Central list to track all bookings for validation
        self.__global_booking_list = [] 

    def add_resident(self, resident):
        self.__resident_list.append(resident)
        
    def add_building(self, building):
        self.__building_list.append(building)

    # --- 1. Search Resident ---
    def search_resident_by_id(self, resident_id):
        for resident in self.__resident_list:
            if resident.id == resident_id:
                return resident
        return None

    # --- 2. Search Building ---
    def search_building_by_id(self, building_id):
        for building in self.__building_list:
            if building.id == building_id:
                return building
        return None

    # --- 3. Search Facility ---
    def search_share_facility_by_id(self, building, share_facility_id):
        for facility in building.share_facility_list:
            if facility.id == share_facility_id:
                return facility
        return None

    # --- 4. Check Availability ---
    def check_availability(self, share_facility_id, booking_time):
        # Loop through global bookings to see if this facility is taken at this time
        for booking in self.__global_booking_list:
            if booking.share_facility_id == share_facility_id and booking.booking_time == booking_time:
                return False # Not Available
        return True # Available

    # --- MAIN METHOD: Booking Logic ---
    def booking_share_facility(self, resident_id, share_facility_id, building_id, booking_time):
        # 1. Search Resident
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return self.showLoginError()

        # 2. Search Building
        building = self.search_building_by_id(building_id)
        if building is None:
            return self.showBuildingIdError()

        # 3. Search Facility
        facility = self.search_share_facility_by_id(building, share_facility_id)
        if facility is None:
            return {"ok": False, "error": "Facility not found"}

        # 4. Check Availability
        is_available = self.check_availability(share_facility_id, booking_time)
        if not is_available:
            return self.showBookingFail("Time slot is already booked")

        # 5. Create Booking
        new_booking = Booking_Share_Facility(resident_id, building_id, share_facility_id, booking_time)

        # 6. Add Booking (to Global list and Resident list)
        self.__global_booking_list.append(new_booking)
        resident.add_booking(new_booking)

        # 7. Success
        return self.showBookingSuccess(new_booking)

    # --- Response Helpers ---
    def showBookingSuccess(self, booking):
        return {
            "ok": True, 
            "message": "Booking Success", 
            "details": {
                "facility": booking.share_facility_id,
                "time": booking.booking_time
            }
        }

    def showBookingFail(self, reason):
        return {"ok": False, "fn": "showBookingFail", "reason": reason}

    def showLoginError(self):
        return {"ok": False, "fn": "showLoginError", "reason": "Resident not found"}

    def showBuildingIdError(self):
        return {"ok": False, "fn": "showBuildingIdError", "reason": "Building not found"}


# ==========================================
#               MOCK DATA
# ==========================================
dorm_system = Dorm("University Dorm")

def setup_mock_data():
    # 1. Create Building & Facility
    b1 = Building("B1", "1")
    meeting_room = Meeting_Room("MR-001", FacilityStatus.Available, "Large")
    b1.add_facility(meeting_room)
    dorm_system.add_building(b1)

    # 2. Create Resident
    r1 = Resident("John Doe", "R001", "john@email.com", "0811111111")
    dorm_system.add_resident(r1)

    print(">>> System Ready.")
    print("    Resident ID: 'R001'")
    print("    Building ID: 'B1'")
    print("    Facility ID: 'MR-001'")

setup_mock_data()


# ==========================================
#               API ZONE
# ==========================================
app = FastAPI()

class BookingRequest(BaseModel):
    resident_id: str
    share_facility_id: str
    building_id: str
    booking_time: str 

@app.post("/booking_share_facility")
async def booking_share_facility(request: BookingRequest):
    """
    Endpoint matches the sequence diagram flow:
    Search Resident -> Search Building -> Search Facility -> Check Time -> Book
    """
    result = dorm_system.booking_share_facility(
        request.resident_id, 
        request.share_facility_id, 
        request.building_id, 
        request.booking_time
    )
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)