from datetime import datetime
from enum import Enum
from .staff import *

class CleaningStatus(Enum):
    REQUESTED = "Requested"
    CLEANING = "Cleaning"
    FINISHED = "Finished"

class CleaningTicket:
    ID = 1
    def __init__(self,resident_id,room_id):
        self.__ticket_id = f"CLTICKET-{CleaningTicket.ID:04d}"
        self.__resident_id = resident_id
        self.__room_id = room_id
        self.__report_time = datetime.now()
        self.__cost = 0
        self.__status = CleaningStatus.REQUESTED
        
        CleaningTicket.ID += 1

    # getter artibute CleaningTicket
    @property
    def id(self):
        return self.__ticket_id
    
    @property
    def status(self):
        return self.__status

