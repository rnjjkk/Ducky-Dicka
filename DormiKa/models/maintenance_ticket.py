from datetime import datetime
from .enum import MaintenanceStatus

class MaintenanceTicket:
    ID = 1

    def __init__(self, reporter, room_id, issue_category, responsible_technician=None):
        self.__id = f'MT-{MaintenanceTicket.ID:04d}'
        self.__reporter = reporter
        self.__room_id = room_id
        self.__issue_category = issue_category
        self.__report_time = datetime.now()
        self.__responsible_technician = responsible_technician
        self.__approve_employee = None
        self.__evidence_before = None
        self.__evidence_after = None
        self.__notes = None
        self.__start_time = None
        self.__status = "IDLE"

        MaintenanceTicket.ID += 1

    @property
    def id(self):
        return self.__id

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
    def issue_category(self):
        return self.__issue_category

    @property
    def responsible_technician(self):
        return self.__responsible_technician

    @property
    def start_time(self):
        return self.__start_time

    @property
    def notes(self):
        return self.__notes

    @property
    def evidence_before(self):
        return self.__evidence_before

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    def update_maintenance_status(self, status):
        self.__status = status

    def begin_work(self, notes: str = None, evidence_before: str = None):
        if self.__status == MaintenanceStatus.IN_PROGRESS:
            raise ValueError(f"Ticket {self.__id} is already in progress")
        if self.__status == MaintenanceStatus.RESOLVED:
            raise ValueError(f"Ticket {self.__id} is already resolved")
        self.__start_time = datetime.now()
        self.__notes = notes
        self.__evidence_before = evidence_before
        self.__status = MaintenanceStatus.IN_PROGRESS

    def approve_maintenance(self, employee, status):
        self.__approve_employee = employee.id
        self.__status = status