from fastapi import FastAPI
import uvicorn
from datetime import datetime
from enum import Enum

class User:
    """
    ### Attributes
    - id
    - name
    - email
    - phone_number
    - strike
    - date_create
    """
    def __init__(self, id, name, email, phone_number):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__strike = None
        self.__date_create = datetime.now()

    @property
    def id(self):
        return self.__id

    @property
    def email(self):
        return self.__email

    @property
    def status(self):
        return self.__status

    @property
    def date_create(self):
        return self.__date_create

class Staff:
    """
    ### Attributes
    - id
    - name
    - building_responsibility
    - role_id ???
    """
    def __init__(self, id, name, email, phone_number, building_responsibility=None, status="ACTIVE"):
        self.__id = id
        self.__name = name
        self.__building_responsibility = building_responsibility
        self.__status = status
        self.__date_create = datetime.now()

    @property
    def id(self):
        return self.__id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

class Dorm:
    """
    ### Attributes
    - name: str
        * dorm name

    ### Methods
    """
    def __init__(self, name):
        self.__name = name
        self.__buildings = []
        self.__applicants = []
        self.__residents = []
        self.__operation_staffs = []
        self.__technicians = []
        self.__building_managers = []
        self.__system_admins = []

    @property
    def maintenance_technician_list(self):
        return self.__technicians

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, os):
        self.__operation_staffs.append(os)

    def add_technician(self, tc):
        self.__technicians.append(tc)

    def search_resident_by_id(self, user_id):
        for resident in self.__residents:
            if int(resident.id[-4:]) == int(user_id):
                return resident
        return None

    def search_available_os(self):
        for os in self.__operation_staffs:
            if os.status == "ACTIVE":
                return os
        return None

    def search_match_tc(self, skl):
        for tc in self.__technicians:
            for skill in tc.skills:
                if skill == skl and tc.status:
                    return tc
        return None

    def request_maintenance(self, resident_id, room_id, issue_category):
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return {"error": "resident not found!"}
        
        staff = self.search_available_os()
        if staff is None:
            return {"error": "no available staff!"}
        
        return staff.start_maintenance(
            resident, 
            self.__technicians, 
            room_id, 
            issue_category
        )

class Resident(User):
    """
    ### Attributes
    - #### Class Attribute
        * ID
    """
    ID = 1

    def __init__(self, name, email: str, phone_number: str, status: str=None):
        super().__init__(f"RS-{datetime.now().year}-{Resident.ID:04d}", name, email, phone_number)
        self.__move_in_date: str = datetime.now()
        self.__booking: list = []
        self.__discount: list = []
        self.__invoice: list = []
        self.__receipt: list= []
        self.__maintenance_ticket: list = []
        self.__status: str = status
        
        Resident.ID += 1

    def add_maintenance_ticket(self, ticket):
        self.__maintenance_ticket.append(ticket)

class Operating_Staff(Staff):
    ID = 1
    
    def __init__(self, name, email, phone_number, status="ACTIVE"):
        super().__init__(f"OS-{datetime.now().year}-{Operating_Staff.ID:04d}", name, email, phone_number, "A01", status)

        Operating_Staff.ID += 1

    def start_maintenance(self, reporter, technicians, room_id, issue_category):
        self.__status = "WORKING"
        
        technician = self.find_available_technician(technicians)
        if technician is None:
            self.__status = "ACTIVE"
            return {"error": "no available technician"}
        
        ticket = self.create_maintenance_ticket(reporter, room_id, issue_category, technician.id)
        technician.assign_ticket(ticket)
        
        ticket.approve_maintenance(self, "APPROVED")
        
        reporter.add_maintenance_ticket(ticket)

        return {
            "reporter": f"{ticket.reporter}",
            "room": f"{ticket.room_id}",
            "technician": f"{ticket.responsible_technician}",
            "status": f"{ticket.status}"
        }

    def find_available_technician(self, technicians):
        for tc in technicians:
            if tc.status == "ACTIVE":
                return tc
        return None

    def create_maintenance_ticket(self, reporter, room_id, issue_category, technician):
        ticket = Maintenance_Ticket(reporter.id, 
                                    room_id, 
                                    issue_category, 
                                    responsible_technician=technician
        )
        return ticket

class Maintenance_Ticket:
    ID = 1

    def __init__(self, reporter, room_id, issue_category, responsible_technician=None):
        self.__id = f"MT-{datetime.today().strftime("%Y%m%d")}-building-{Maintenance_Ticket.ID:04d}"
        self.__reporter = reporter
        self.__room_id = room_id
        self.__issue_category = issue_category
        self.__report_time = datetime.now()
        self.__responsible_technician = responsible_technician
        self.__approve_staff = None
        self.__evidence_before_after = None
        self.__status = "IDLE"

        Maintenance_Ticket.ID += 1

    @property
    def reporter(self):
        return self.__reporter

    @reporter.setter
    def reporter(self, reporter):
        self.__reporter = reporter

    @property
    def room_id(self):
        return self.__room_id

    @property
    def responsible_technician(self):
        return self.__responsible_technician

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    def update_maintenance_status(self, status):
        self.__status = status

    def approve_maintenance(self, staff, status):
        self.__approve_staff = staff.id
        self.__status = status

class Maintenance_Technician:
    ID = 1

    def __init__(self, skills: list, schedule=None, current_mt=None, status="ACTIVE"):
        self.__id = f"TC-{datetime.now().year}-{Maintenance_Technician.ID:04d}"
        self.__skills = skills
        self.__schedule = None
        self.__current_mt = current_mt
        self.__status = status

        Maintenance_Technician.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def skills(self):
        return self.__skills

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        self.__status = new_status

    def assign_ticket(self, ticket):
        self.__status = "WORKING"
        self.__current_mt = ticket

        ticket.update_maintenance_status("FINISH")
        self.__status = "ACTIVE"
        return "done"

"""========================================================================================================================"""

dorm = Dorm("Ducky")
kenny = Resident("kenny", "ken@gmail.com", "1234567890")
john = Resident("john", "john@gmail.com", "1234567890")
dorm.add_resident(kenny)
dorm.add_resident(john)

# print(f"\n{kenny.id}\n")

tom = Operating_Staff("tom", "tom@gmail.com", "1234567890", status="ACTIVE")
dorm.add_operation_staff(tom)

tech = Maintenance_Technician("tech", "tech@gmail.com", "1234567890",status="ACTIVE")
dorm.add_technician(tech)

# resident = None

# resi = dorm.search_resident_by_id(1)
# if resi is None:
#     pass
#     # return "resident not found"
# print(resi)
# os = dorm.search_available_os()
# if os is None:
#     pass
#     # return "no available staaff"
# print(os)
# tech_list = dorm.maintenance_technician_list
# print(tech_list)
# response = None 
# try:
#     response = dorm.request_maintenance(resi, os, tech_list, "001", "PLUMBING")
# except ValueError as e:
#     pass
#     # return f"{e}"
# # return f"{response}"

"""========================================================================================================================"""

"""
1
RM-Standard-A01-08-0001
PLUMBING
"""

app = FastAPI()

@app.post("/request-maintenance")
async def request_maintenance(resident_id, room_id, issue_category):
    res = dorm.request_maintenance(resident_id, room_id, issue_category)
    return res

if __name__ == "__main__":
    uvicorn.run("maintenance_req:app", host="127.0.0.1",port=8000, log_level="info", reload=True)