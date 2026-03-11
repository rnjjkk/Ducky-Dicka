class Building:
    ID = 1
    
    def __init__(self, floor_count, zone):
        self.__id = f"{zone}{Building.ID:02d}"
        self.__floor_count = floor_count
        self.__rooms = []
        self.__washing_machines = []
        self.__meeting_rooms = []
        self.__lockers = []

        Building.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def rooms(self):
        return self.__rooms

    def add_room(self, room):
        self.__rooms.append(room)
        return self.__rooms

    def __iter__(self):
        return iter(self.__rooms)
    
    def get_share_facility_by_id(self, facility_id):
        for sf in self.share_facility_list:
            if sf.id == facility_id:
                return sf
        raise ValueError("Share facility not found")

