from datetime import datetime
from .enum import *
from .maintenance_ticket import *
from .invoice import Invoice
from .member import Standard_Member, Plus_Member, Platinum_Member

class Employee:
    ID = 1

    def __init__(self, name):
        self.__id = f"EM-{Employee.ID:04d}"
        self.__date_create = datetime.now()
        self.__name = name
        self.__status = AvailabilityStatus.AVAILABLE

        Employee.ID += 1

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id
    
    @property
    def status(self):
        return self.__status

    def start_maintenance(self, reporter, technicians, room, issue_category):
        self.__status = AvailabilityStatus.UNAVAILABLE

        technician = self.find_available_technician(technicians)
        
        ticket = self.create_maintenance_ticket(reporter, room.id, issue_category, technician.id)
        technician.assign_ticket(ticket)
        room.add_maintenance_ticket(ticket)
        ticket.status = MaintenanceStatus.REPORTED

        return {
            "reporter": f"{ticket.reporter}",
            "room": f"{ticket.room_id}",
            "technician": f"{ticket.responsible_technician}",
            "status": f"{ticket.status.value}"
        }

    def find_available_technician(self, technicians):
        for tc in technicians:
            if tc.status == AvailabilityStatus.AVAILABLE:
                return tc
        self.__status = AvailabilityStatus.AVAILABLE
        raise Exception("no available technician")

    def create_maintenance_ticket(self, reporter, room_id, issue_category, technician):
        ticket = MaintenanceTicket(reporter.id, 
                                    room_id, 
                                    issue_category, 
                                    responsible_technician=technician
        )
        return ticket
    

    def create_contract_invoice(self, monthly_rent, room_id):
        return Invoice(InvoiceType.CONTRACT, monthly_rent, InvoiceStatus.UNPAID, room_id)

    def asign_member(self, resident, type):
        member_type = MemberType(type.strip().upper())
        match member_type:
            case MemberType.STANDARD:
                member = Standard_Member()
            case MemberType.PLUS:
                member = Plus_Member()
            case MemberType.PLATINUM:
                member = Platinum_Member()
            case _:
                raise ValueError("type_member : format error")
        resident.set_member(member)
        price = MemberPrice[member_type.name].value
        return Invoice(InvoiceType.MEMBER, price, InvoiceStatus.UNPAID)
