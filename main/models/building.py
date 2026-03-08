class Building:
    ID = 1
    
    def __init__(self, floor):
        self.__id = Building.ID
        self.__floor = floor
        self.__rooms = []
        self.__washing_machines = []
        self.__meeting_rooms = []
        self.__lockers = []

        Building.ID += 1

    @property
    def add_room(self, room):
        self.__rooms.append(room)
        return self.__rooms