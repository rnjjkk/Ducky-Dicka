from datetime import datetime

class Employee:
    ID = 1
    
    def __init__(self, name):
        self.__id = Employee.ID
        self.__date_create = datetime.now()
        self.__name = name

        Employee.ID += 1