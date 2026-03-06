from datetime import datetime

class Employee:
    ID = 1
    
    def __init__(self, name):
        self.__id = Employee.ID
        self.__date_create = datetime.now()
        self.__name = name
        # self.__status = None

        Employee.ID += 1

    @property
    def fid(self):
        return f"EM-{self.__date_create.year}-{self.__id:04d}"