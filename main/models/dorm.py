class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technician: list = []
        self.__cleaner: list = []

    def search_resident_by_id(self, id):
        for resident in self.__residents:
            if resident.id == id:
                return resident
        return None

    def search_room_by_id(self, id):
        for building in self.__buildings:
            for room in building:
                if room.id == id:
                    return room
        return None