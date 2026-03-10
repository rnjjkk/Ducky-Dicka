from datetime import datetime, timedelta
from .staff import *

class CleaningStatus:
    Request = "REQUEST"
    Cleaning = "CLEANING"
    Finished = "FINISHED"

class CleaningTicket:
    ID = 1
    def __init__(self,reporter_id,room_id):
        self.__id = CleaningTicket.ID
        self.__reporter_id = reporter_id
        self.__room_id = room_id
        self.__report_time = datetime.now()
        self.__repondsible_cleaner = None
        self.__cost = 0
        self.__status = CleaningStatus.Request
        
        CleaningTicket.ID += 1

    # getter artubute CleaningTicket 
    def fid(self):
        return f"CS-{self.__report_time}-{self.__id:04d}"

    def id(self):
        return self.__id
    
    def report_time(self):
        return self.__report_time
    
    def status(self):
        return self.__status
    
