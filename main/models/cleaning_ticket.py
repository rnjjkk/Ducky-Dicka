from datetime import datetime, timedelta
from .staff import *
class CleaningStatus:
    Request = "REQUEST"
    Cleaning = "CLEANING"
    Finished = "FINISHED"

class CleaningTicket:
    ID = 1
    def __init__(self,room,status = CleaningStatus.Request):
        self.__id = CleaningTicket.ID
        self.__room = room
        self.__report_time = datetime.now()
        self.__repondsible_cleaner = None
        self.__cost = 0
        self.__status = status
    ID += 1

    