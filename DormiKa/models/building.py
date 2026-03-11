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

    def find_and_hold_available_room_by_type(self, room_type):
        from .enum import RoomStatus
        for room in self.__rooms:
            if room.type == room_type and room.status == RoomStatus.AVAILABLE:
                room.hold(48)
                return room
        raise LookupError(f"No available room of type '{room_type.value}' in building {self.__id}")

    def __iter__(self):
        return iter(self.__rooms)
    
def get_share_facility_by_id(self, facility_id):
    all_facilities = self.__washing_machines + self.__meeting_rooms
    for sf in all_facilities:
        if sf.id == facility_id:
            return sf
    raise ValueError("Share facility not found")

# เพิ่ม method add สำหรับแต่ละประเภท
def add_washing_machine(self, wm):
    self.__washing_machines.append(wm)

def add_meeting_room(self, mr):
    self.__meeting_rooms.append(mr)

