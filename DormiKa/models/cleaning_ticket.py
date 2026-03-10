from datetime import datetime
from enum import Enum
from .staff import *

class CleaningStatus(Enum):
    REQUESTED = "Requested"
    CLEANING = "Cleaning"
    FINISHED = "Finished"

class CleaningTicket:
    ID = 1
    def __init__(self,reporter_id,room_id):
        self.__ticket_id = CleaningTicket.ID
        self.__reporter_id = reporter_id
        self.__room_id = room_id
        self.__report_time = datetime.now()
        self.__cost = 0
        self.__status = CleaningStatus.REQUESTED
        
        CleaningTicket.ID += 1

    # getter artibute CleaningTicket
    @property
    def fid(self):
        return f"CLTICKET-{self.__ticket_id:04d}"

