from models.dorm import Dorm
from models.resident import Resident
from models.building import Building
from models.room import Room
from models.contract import Contract
from models.employee import Employee
from models.staff import Cleaner, PlumbingTech, ElectricalTech, ACTech

from models.enum import *

def init_mock_data():
    global dorm
    dorm = Dorm("DormiKa")

    building = Building(floor_count=5, zone="A")
    dorm.add_building(building)

    rooms = [
        Room(building, 1, RoomType.STUDIO_ROOM, RoomStatus.AVAILABLE, rental=6700),
        Room(building, 2, RoomType.STUDIO_ROOM, RoomStatus.AVAILABLE, rental=6700),

        Room(building, 3, RoomType.STANDARD_ROOM, RoomStatus.AVAILABLE, rental=8200),
        Room(building, 4, RoomType.STANDARD_ROOM, RoomStatus.AVAILABLE, rental=8200),

        Room(building, 5, RoomType.ONE_BED_ROOM, RoomStatus.AVAILABLE, rental=10500),
    ]
    for room in rooms:
        dorm.add_room(room)

    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Kenny"]
    for i in range(len(names)):
        resident = Resident(
            name=names[i],
            email=f"{names[i].lower()}@example.com",
            phone_number=f"123-456-789{i}"
        )
        dorm.add_resident(resident)

    resident = dorm.residents[0]
    room = dorm.buildings[0].rooms[0]
    contract = Contract(resident, room)
    resident.add_contract(contract)
    room.status = RoomStatus.OCCUPIED

    names = ["Harry", "Sally", "Tom", "Lucy", "Mia", "Oscar"]
    for i in range(len(names)):
        employee = Employee(
            name=names[i],
        )
        dorm.add_employee(employee)

    names = ["John", "Jane"]
    for i in range(len(names)):
        cleaner = Cleaner(
            name=names[i],
            phone_number=f"555-123-456{i}",
            cleaning_supplies_list=["Broom", "Mop"],
            assigned_rooms=[]
        )
        dorm.add_cleaner(cleaner)

    names = ["Mike", "Sara", "Leo"]
    technicians = [
        ElectricalTech(
        name=names[i],
        phone_number=f"555-987-654{i}",
        capabilities=["Electrical", "Plumbing"],
        schedule=None,
        current_task=None,
        status=AvailabilityStatus.AVAILABLE
    ),
        PlumbingTech(
        name=names[i],
        phone_number=f"555-987-654{i}",
        capabilities=["Plumbing"],
        schedule=None,
        current_task=None,
        status=AvailabilityStatus.AVAILABLE
    ),
        ACTech(
        name=names[i],
        phone_number=f"555-987-654{i}",
        capabilities=["AC Maintenance"],
        schedule=None,
        current_task=None,
        status=AvailabilityStatus.AVAILABLE
    )
    ]
    for t in technicians:
        dorm.add_technician(t)

if __name__ == "__main__":
    init_mock_data()