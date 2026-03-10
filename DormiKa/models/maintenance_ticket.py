from datetime import datetime

class MaintenanceStatus:
    pass

class MaintenanceTicket:
    ID = 1

    def __init__(self, reporter, room_id, issue_category, responsible_technician=None):
        self.__id = f'MT-{self.__report_time.strftime("%Y%m%d")}-{MaintenanceTicket.ID:04d}'
        self.__reporter = reporter
        self.__room_id = room_id
        self.__issue_category = issue_category
        self.__report_time = datetime.now()
        self.__responsible_technician = responsible_technician
        self.__approve_employee = None
        self.__evidence_before_after = None
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

    def approve_maintenance(self, employee, status):
        self.__approve_employee = employee.id
        self.__status = status