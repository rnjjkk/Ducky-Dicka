from datetime import datetime
from enum import Enum
from .staff import *
from .enum import CleaningStatus
class CleaningTicket:
    ID = 1
    def __init__(self,resident_id,room_id):
        self.__ticket_id = f"CLTICKET-{CleaningTicket.ID:04d}"
        self.__resident_id = resident_id
        self.__room_id = room_id
        self.__report_time = datetime.now()
        self.__cost = 100
        self.__status = CleaningStatus.REQUESTED
        
        CleaningTicket.ID += 1

    # getter artibute CleaningTicket
    @property
    def id(self):
        return self.__ticket_id
    
    @property
    def room_id(self):
        return self.__room_id
    
    @property
    def report_time(self):
        return self.__report_time
    
    @property
    def cost(self):
        return self.__cost
    
    @property
    def status(self):
        return self.__status

