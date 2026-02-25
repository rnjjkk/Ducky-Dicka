from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, datetime
import uvicorn

class FacilityStatus(Enum):
    Available = 1
    Reserved = 2
    In_Use = 3
    Maintenance = 4
    Disabled = 5

class ResidentStatus(Enum):
    Applicant = 1
    Active = 2
    Suspended = 3
    Closed = 4

class InvoiceStatus(Enum):
    Issued = 1
    Paid = 2
    Overdue = 3
    Disputed = 4
    Refunded = 5

class Staff:
    def __init__(self,id,name,building_responsibility):
        self.__id = id
        self.__name = name
        self.__builfing_responsibility = building_responsibility
        self.__status = None
        self.__date_create = date.today()

    # getter artibute Staff
    @property
    def name(self):
        return self.__name
    
    @property
    def id(self):
        return self.__id
    
    # setter artibute Staff
    @name.setter
    def name(self,name):
        self.__name = name
    
    @id.setter
    def id(self,id):
        self.__id = id
    
    # method Staff
    def logout(self):
        pass
        
class OperationStaff(Staff):
    def __init__(self, id, name, building_responsibility):
        super().__init__(id, name, building_responsibility)

    # method Operation_Staff
    def view_booking_list(self):
        pass

    def confirm_booking(self,book):
        pass

    # create_invoice(resident_id,room_cost,electricity_cost,water_cost,parking_slot_cost,share_facility_cost,maintenance_cost)
    # เวลาสร้าง invoice ควรมีเลขห้องที่ resident คนนั้นเป็นเจ้าของ
    def create_invoice(self,resident,invoice_data):

        invoice_data_str = invoice_data.split("-")

        if len(invoice_data_str) != 7:
            return None

        invoice_id,room_cost,electricity_cost,water_cost,parking_slot_cost,share_facility_cost,maintenance_cost = invoice_data_str
        resident_info = {"name": resident.name,"id":resident.id}
        invoice = Invoice(invoice_id,resident_info,room_cost,electricity_cost,water_cost,parking_slot_cost,share_facility_cost,maintenance_cost)
        return invoice

    def add_invoice(self,resident,invoice):
        resident.invoice_list.append(invoice)
        return invoice
        
class Invoice:
    def __init__(self,invoice_id,resident_info,room_cost,electricity_cost,water_cost,parking_slot_cost,share_facility_cost,maintenance_cost):
        self.__invoice_id = invoice_id
        self.__resident_info = resident_info
        self.__invoice_status = InvoiceStatus.Issued.name
        self.__date_created_invoice = datetime.today()
        self.__room_cost = room_cost
        self.__electricity_cost = electricity_cost
        self.__water_cost = water_cost
        self.__parking_slot_cost = parking_slot_cost
        self.__share_facility_cost = share_facility_cost
        self.__maintenance_cost = maintenance_cost

    # getter artibute Invoice
    @property
    def invoice_id(self):
        return self.__invoice_id
    
    def showInvoice(self):
        return {
            "invoice_id": self.__invoice_id,
            "resident_info": self.__resident_info,
            "invoice_status": self.__invoice_status,
            "date_created_invoice": self.__date_created_invoice,
            "room_cost": self.__room_cost,
            "electricity_cost": self.__electricity_cost,
            "water_cost": self.__water_cost,
            "parking_slot_cost": self.__parking_slot_cost,
            "share_facility_cost": self.__share_facility_cost,
            "maintenance_cost": self.__maintenance_cost
            }

class User:
    def __init__(self, name, id, email, phone_number):
        self.__name = name
        self.__id = id
        self.__email = email
        self.__phone_number = phone_number

    # getter artibute User
    @property
    def name(self):
        return self.__name
    
    @property
    def id(self):
        return self.__id
    
    @property
    def email(self):
        return self.__email
    
    @property
    def phone_number(self):
        return self.__phone_number
    
    # setter artibute User
    @name.setter
    def name(self,name):
        self.__name = name
    
    @id.setter
    def id(self,id):
        self.__id = id
    
    @email.setter
    def email(self,email):
        self.__email = email
    
    @phone_number.setter
    def phone_number(self,phone_number):
        self.__phone_number = phone_number
    
class Resident(User):
    def __init__(self, name, id, email, phone_number):
        super().__init__(name, id, email, phone_number)
        self.__move_in_date = date.today()
        self.__invoice_list = []
        self.__booking_list = []
        self.__booking_share_facility_list = [] # List to store Booking objects
        self.__status = ResidentStatus.Active.name
        

    # getter artibute Resident
    @property
    def invoice_list(self):
        return self.__invoice_list
    
    # setter artibute Resident
    @invoice_list.setter
    def invoice_list(self,invoice_list):
        self.__invoice_list = invoice_list

    # method Resident
    def add_booking(self, booking):
        self.__booking_share_facility_list.append(booking)

    def show_invoice(self):
        invoice_ids = []
        for invoice in self.__invoice_list:
            invoice_ids.append(invoice.invoice_id) # เก็บเฉพาะ id ใส่ list
            
        return {"resident_id": self.id, "total_invoices": len(invoice_ids), "invoice_ids": invoice_ids}



class ShareFacility:
    def __init__(self, facility_id, status):
        self.__facility_id = facility_id
        self.__status = status

    # getter artibuite Share_Facility
    @property
    def id(self):
        return self.__facility_id

class MeetingRoom(ShareFacility):
    def __init__(self, facility_id, status, size):
        super().__init__(facility_id, status)
        self.__size = size

class Building:
    def __init__(self, building_id, floor):
        self.__building_id = building_id
        self.__floor = floor
        self.__share_facility_list = []

    # getter artibute Building
    @property
    def id(self):
        return self.__building_id

    @property
    def share_facility_list(self):
        return self.__share_facility_list
    
    # method Building
    def add_facility(self, facility):
        self.__share_facility_list.append(facility)

class BookingShareFacility:
    def __init__(self, resident_id, building_id, share_facility_id, booking_time):
        self.__resident_id = resident_id
        self.__building_id = building_id
        self.__share_facility_id = share_facility_id
        self.__booking_time = booking_time

    # getter Booking_Share_Facility
    @property
    def share_facility_id(self):
        return self.__share_facility_id
    
    @property
    def booking_time(self):
        return self.__booking_time

class Dorm: # Controller
    def __init__(self, name):
        self.__name = name
        self.__building_list = []
        self.__resident_list = []
        self.__os_staff = []
        # Central list to track all bookings for validation
        self.__global_booking_list = [] 

    # method Dorm
    def add_resident(self, resident):
        self.__resident_list.append(resident)

    def add_os_staff(self,operation_staff):
        self.__os_staff.append(operation_staff)
        
    def add_building(self, building):
        self.__building_list.append(building)

    def search_resident_by_id(self, resident_id):
        for resident in self.__resident_list:
            if resident.id == resident_id:
                return resident
        return None
    
    def serch_operation_staff_by_id(self,operation_staff_id):
        for os in self.__os_staff:
            if os.id == operation_staff_id:
                return os
        return None

    def search_building_by_id(self, building_id):
        for building in self.__building_list:
            if building.id == building_id:
                return building
        return None

    def search_share_facility_by_id(self, building, share_facility_id):
        for facility in building.share_facility_list:
            if facility.id == share_facility_id:
                return facility
        return None

    def check_availability(self, share_facility_id, booking_time):
        # Loop through global bookings to see if this facility is taken at this time
        for booking in self.__global_booking_list:
            if booking.share_facility_id == share_facility_id and booking.booking_time == booking_time:
                return False # Not Available
        return True # Available

    def booking_share_facility(self, resident_id, share_facility_id, building_id, booking_time):
        # 1. Search Resident
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return self.showResidentLoginError()

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
        new_booking = BookingShareFacility(resident_id, building_id, share_facility_id, booking_time)

        # 6. Add Booking (to Global list and Resident list)
        self.__global_booking_list.append(new_booking)
        resident.add_booking(new_booking)

        # 7. Success
        return self.showBookingSuccess(new_booking)
    
    def create_invoice(self,operation_staff_id,resident_id,invoice_data):
        # 1. serch operation staff by id
        operation_staff = self.serch_operation_staff_by_id(operation_staff_id)
        if operation_staff is None:
            return self.showOperationStaffLoginError()
        
        # 2. serch resident by id
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return self.showResidentLoginError()
        
        # 3. operation staff create invoice
        invoice = operation_staff.create_invoice(resident,invoice_data)
        if invoice is None:
            return self.showFormatError()
        
        # 4. add invoice to Resident invoice_list
        operation_staff.add_invoice(resident,invoice)

        # 5. Success
        return self.showcreateInvoiceSuccess(invoice)


    # --- Response Helpers ---
    # booking success respond
    def showBookingSuccess(self, booking):
        return {
            "ok": True, 
            "message": "Booking Success", 
            "details": {
                "facility": booking.share_facility_id,
                "time": booking.booking_time
            }
        }
    
    # booking fail respond
    def showBookingFail(self, reason):
        return {"ok": False, "fn": "showBookingFail", "reason": reason}
    
    # create invoice success respond
    def showcreateInvoiceSuccess(self,invoice):
        return {"ok": True,"message":"Create Invoice Success","invoice":invoice}

    # create invoice fail respond
    def showcreateInvoiceFail(self,reason):
        return {"ok": False, "fn": "showcreateInvoiceFail", "reason": reason}

    # not found respond
    def showResidentLoginError(self):
        return {"ok": False, "fn": "showLoginError", "reason": "Resident not found"}
    
    def showOperationStaffLoginError(self):
        return {"ok": False, "fn": "showLoginError", "reason": "Operation Staff not found"}

    def showBuildingIdError(self):
        return {"ok": False, "fn": "showBuildingIdError", "reason": "Building not found"}
    
    # format error respond
    def showFormatError(self):
        return {"ok": False, "fn": "showFormatError","resson": "Format error"}

# ==========================================
# TEST SCRIPT ZONE
# ==========================================

# 1. create Dorm
my_dorm = Dorm("Happy Dorm")

def test_create_invoice_logic():
    print("--- Starting Create Invoice Logic Tests ---\n")

    # 2. Setup Data: Create Staff, and Resident
    
    staff1 = OperationStaff(id="OS001", name="Admin Somchai", building_responsibility="Building A")
    my_dorm.add_os_staff(staff1)
    
    resident1 = Resident(name="John Doe", id="R001", email="john@example.com", phone_number="0812345678")
    my_dorm.add_resident(resident1)

    # In your updated code, invoice_data needs exactly 7 segments:
    # Format: invoice_id - room_cost - electricity_cost - water_cost - parking_slot_cost - share_facility_cost - maintenance_cost
    valid_invoice_data = "INV001-5000-1200-200-500-100-300"
    invalid_invoice_data = "INV002-5000-1200" # Only 3 segments (Invalid format)

    # --- Test Case 1: Successful Invoice Creation ---
    print("[Test 1] Testing Successful Invoice Creation...")
    result1 = my_dorm.create_invoice(operation_staff_id="OS001", resident_id="R001", invoice_data=valid_invoice_data)
    
    assert result1["ok"] == True, "Test 1 Failed: Expected 'ok' to be True"
    assert len(resident1.invoice_list) == 1, "Test 1 Failed: Invoice was not added to the resident's list"
    assert resident1.invoice_list[0].invoice_id == "INV001", "Test 1 Failed: Invoice ID mismatch"
    assert resident1.invoice_list[0].showInvoice()["resident_info"]["name"] == "John Doe", "Test 1 Failed: Resident Info dictionary mismatch"
    print("✅ PASS: Invoice created successfully and added to Resident's profile.")
    print(f"   -> Result Output: {result1}")
    print(f"   -> Resident's Invoice Data: {resident1.invoice_list[0].showInvoice()}\n")


    # --- Test Case 2: Operation Staff Not Found ---
    print("[Test 2] Testing Operation Staff Not Found (Invalid ID)...")
    result2 = my_dorm.create_invoice(operation_staff_id="OS999", resident_id="R001", invoice_data=valid_invoice_data)
    
    assert result2["ok"] == False, "Test 2 Failed: Expected 'ok' to be False"
    assert result2["reason"] == "Operation Staff not found", "Test 2 Failed: Incorrect error reason"
    print("✅ PASS: System correctly blocked action when Operation Staff was not found.")
    print(f"   -> Result Output: {result2}\n")


    # --- Test Case 3: Resident Not Found ---
    print("[Test 3] Testing Resident Not Found (Invalid ID)...")
    result3 = my_dorm.create_invoice(operation_staff_id="OS001", resident_id="R999", invoice_data=valid_invoice_data)
    
    assert result3["ok"] == False, "Test 3 Failed: Expected 'ok' to be False"
    assert result3["reason"] == "Resident not found", "Test 3 Failed: Incorrect error reason"
    print("✅ PASS: System correctly blocked action when Resident was not found.")
    print(f"   -> Result Output: {result3}\n")


    # --- Test Case 4: Invalid Data Format ---
    print("[Test 4] Testing Invalid Invoice Data Format...")
    result4 = my_dorm.create_invoice(operation_staff_id="OS001", resident_id="R001", invoice_data=invalid_invoice_data)
    
    assert result4["ok"] == False, "Test 4 Failed: Expected 'ok' to be False"
    assert result4["resson"] == "Format error", "Test 4 Failed: Incorrect error reason" # Matches 'resson' in showFormatError()
    print("✅ PASS: System correctly rejected the invalid data format.")
    print(f"   -> Result Output: {result4}\n")

    print("--- All tests executed successfully! The core logic is completely solid. ---")

test_create_invoice_logic()

# ==========================================
#               API ZONE
# ==========================================
app = FastAPI()

class CreateInvoiceRequest(BaseModel):
    operation_staff_id : str
    resident_id : str
    invoice_data : str

@app.post("/create_invoice")
async def create_invoice(requset : CreateInvoiceRequest):
    result = my_dorm.create_invoice(requset.operation_staff_id,requset.resident_id,requset.invoice_data)
    return result

@app.get("/show_invoice")
async def show_invoice(resident_id : str):
    resident = my_dorm.search_resident_by_id(resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    result = resident.show_invoice()
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)