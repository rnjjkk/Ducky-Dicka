from datetime import datetime
from .enum import AvailabilityStatus, InvoiceType, InvoiceStatus
from .maintenance_ticket import MaintenanceTicket
from .invoice import Invoice

class Employee:
    ID = 1

    def __init__(self, name):
        self.__id = f"EM-{Employee.ID:04d}"
        self.__date_create = datetime.now()
        self.__name = name
        self.__status = AvailabilityStatus.AVAILABLE

        Employee.ID += 1

    @property
    def fid(self):
        return f"EM-{self.__date_create.year}-{self.__id[-4:]}"

    @property
    def id(self):
        return self.__id
    
    @property
    def status(self):
        return self.__status

    def start_maintenance(self, reporter, technicians, room, issue_category):
        self.__status = "WORKING"
        
        technician = self.find_available_technician(technicians)
        
        ticket = self.create_maintenance_ticket(reporter, room.id, issue_category, technician.id)
        technician.assign_ticket(ticket)
        
        ticket.approve_maintenance(self, "APPROVED")
        self.__status = "AVAILABLE"
        
        room.add_maintenance_ticket(ticket)

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
        self.__status = "AVAILABLE"
        raise Exception("no available technician")

    def create_maintenance_ticket(self, reporter, room_id, issue_category, technician):
        ticket = MaintenanceTicket(reporter.id, 
                                    room_id, 
                                    issue_category, 
                                    responsible_technician=technician
        )
        return ticket
    
    def create_contract_invoice(self, monthly_rent, room_id):
        return Invoice(InvoiceType.CONTRACT, room_id, monthly_rent, InvoiceStatus.UNPAID)