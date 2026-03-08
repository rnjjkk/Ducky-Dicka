class Building:
    ID = 1
    
    def __init__(self, floor, zone="A"):
        self.__id = f"{zone}{Building.ID}"
        self.__floor = floor
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
