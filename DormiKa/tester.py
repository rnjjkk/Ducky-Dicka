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
    dorm = Dorm("========== DormiKa ==========")
    print(dorm.name)

    building = Building(floor_count=5, zone="A")
    dorm.add_building(building)
    print(f"Building ID: {building.id}\n")

    rooms = [
        Room(building, 1, RoomType.STUDIO_ROOM, RoomStatus.AVAILABLE),
        Room(building, 2, RoomType.STUDIO_ROOM, RoomStatus.AVAILABLE),

        Room(building, 3, RoomType.STANDARD_ROOM, RoomStatus.AVAILABLE),
        Room(building, 4, RoomType.STANDARD_ROOM, RoomStatus.AVAILABLE),

        Room(building, 5, RoomType.ONE_BED_ROOM, RoomStatus.AVAILABLE),
    ]
    for room in rooms:
        building.add_room(room)
        print(f"Added Room ID: {room.id}, Type: {room.type.value}, Rent: {room.monthly_rent}\n")

    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Kenny"]
    for i in range(len(names)):
        resident = Resident(
            name=names[i],
            email=f"{names[i].lower()}@example.com",
            phone_number=f"123-456-789{i}"
        )
        dorm.add_resident(resident)
        print(f"Added Resident: {resident.name}".ljust(25   ), end="")
        print(f"{resident.id}")

    resident = dorm.residents[0]
    room = dorm.buildings[0].rooms[0]
    contract = Contract(resident, room)
    resident.add_contract(contract)
    room.status = RoomStatus.OCCUPIED
    print(f"\nAdded {contract.id} to {resident.id}")

    names = ["Harry", "Sally", "Tom", "Lucy", "Mia", "Oscar"]
    for i in range(len(names)):
        employee = Employee(
            name=names[i],
        )
        dorm.add_employee(employee)
        print(f"Added Employee: {employee.name}".ljust(25), end="")
        print(f"{employee.id}")

    names = ["John", "Jane"]
    for i in range(len(names)):
        cleaner = Cleaner(
            name=names[i],
            phone_number=f"555-123-456{i}",
            cleaning_supplies_list=["Broom", "Mop"],
            assigned_rooms=[]
        )
        dorm.add_cleaner(cleaner)
        print(f"Added Cleaner: {cleaner.name}".ljust(25), end="")
        print(f"{cleaner.id}")

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
        print(f"Added Technician: {t.name}".ljust(25), end="")
        print(f"{t.id}")

"""======================================="""

init_mock_data()

print("")

dorm.system_contract_invoice("EM-0001")