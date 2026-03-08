from datetime import datetime
from .maintenance_ticket import *

class Employee:
    ID = 1
    
    def __init__(self, name):
        self.__id = Employee.ID
        self.__date_create = datetime.now()
        self.__name = name
        self.__status = 'AVAILABLE'

        Employee.ID += 1

    @property
    def fid(self):
        return f"EM-{self.__date_create.year}-{self.__id:04d}"

    @property
    def id(self):
        return self.__id
    
    @property
    def status(self):
        return self.__status

    def start_maintenance(self, reporter, technicians, room_id, issue_category):
        self.__status = "WORKING"
        
        technician = self.find_available_technician(technicians)
        if technician is None:
            self.__status = "AVAILABLE"
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
            if tc.status == "AVAILABLE":
                return tc
        return None

    def create_maintenance_ticket(self, reporter, room_id, issue_category, technician):
        ticket = MaintenanceTicket(reporter.id, 
                                    room_id, 
                                    issue_category, 
                                    responsible_technician=technician
        )
        return ticket