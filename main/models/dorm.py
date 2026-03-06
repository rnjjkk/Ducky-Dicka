class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technicians: list = []
        self.__cleaner: list = []

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, employee):
        self.__employees.append(employee)

    def add_technician(self, technician):
        self.__technicians.append(technician)

    def search_resident_by_id(self, id):
        for resident in self.__residents:
            if resident.id == id:
                return resident
        return None

    def search_room_by_id(self, id):
        for building in self.__buildings:
            for room in building:
                if room.id == id:
                    return room
        return None

    def search_available_employee(self):
        for employee in self.__employees:
            if employee.status == "AVAILABLE":
                return employee
        return None

    def request_maintenance(self, resident_id, room_id, issue_category):
        pass