from datetime import datetime

class Staff:
    pass

class Cleaner(Staff):
    pass

class Technician(Staff):
    ID = 1

    def __init__(self, compabilities: list, schedule=None, current_mt=None, status="AVAILABLE"):
        self.__id = f"TC-{datetime.now().year}-{Technician.ID:04d}"
        self.__compabilities = compabilities
        self.__schedule = None
        self.__current_mt = current_mt
        self.__status = status

        Technician.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def compabilities(self):
        return self.__compabilities

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
        self.__status = "AVAILABLE"
        return "done"

class ElectricalTech(Technician):
    pass

class PlumbingTech(Technician):
    pass

class ACTech(Technician):
    pass
