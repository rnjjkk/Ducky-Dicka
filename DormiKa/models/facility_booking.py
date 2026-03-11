from datetime import datetime

class FacilityBooking:
    ID = 1
    
    def __init__(self, resident_id, building_id, facility_id, facility_name, booking_time):
        self.__booking_id = f"FBOOK-{FacilityBooking.ID:04d}"
        self.__resident_id = resident_id
        self.__building_id = building_id
        self.__facility_id = facility_id
        self.__facility_name = facility_name
        self.__booking_time = booking_time
        self.__created_at = datetime.now()
        
        FacilityBooking.ID += 1
    
    @property
    def id(self):
        return self.__booking_id
    
    @property
    def resident_id(self):
        return self.__resident_id
    
    @property
    def building_id(self):
        return self.__building_id
    
    @property
    def facility_id(self):
        return self.__facility_id
    
    @property
    def facility_name(self):
        return self.__facility_name
    
    @property
    def booking_time(self):
        return self.__booking_time
    
    @property
    def created_at(self):
        return self.__created_at