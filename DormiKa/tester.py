from models.dorm import Dorm
from models.resident import Resident
from models.building import Building
from models.room import Room
from models.contract import Contract
from models.employee import Employee
from models.staff import Cleaner, PlumbingTech, ElectricalTech, ACTech

from models.enum import *
from pprint import pprint


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
        print(
            f"Added Room ID: {room.id}, Type: {room.type.value}, Rent: {room.monthly_rent}\n")

    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Kenny"]
    for i in range(len(names)):
        resident = Resident(
            name=names[i],
            email=f"{names[i].lower()}@example.com",
            phone_number=f"123-456-789{i}"
        )
        dorm.add_resident(resident)
        print(f"Added Resident: {resident.name}".ljust(25), end="")
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

def print_all_data():
    print("\n=== All Residents ===")
    for resident in dorm.residents:
        print(f"{resident.id}: {resident.name}")
        if (resident.contracts):
            for contract in resident.contracts:
                print(f"  - Contract ID: {contract.id}, Room: {contract.room.id}, Status: {contract.status.value}")

    print("\n=== All Employees ===")
    for employee in dorm.employees:
        print(f"{employee.id}: {employee.name}")

    print("\n=== All Cleaners ===")
    for cleaner in dorm.cleaners:
        print(f"{cleaner.id}: {cleaner.name} - {cleaner.phone_number}")

    print("\n=== All Technicians ===")
    for tech in dorm.technicians:
        print(f"{tech.id}: {tech.name} - {tech.phone_number} - Capabilities: {', '.join(tech.capabilities)}")

def run_tests():
    print("\n=== System Contract Invoice ===")
    res = dorm.system_contract_invoice("EM-0001")
    pprint(res)

    print("\n=== Sign Contract ===")
    dorm.sign_in(
        "Fill",
        "fill@gmail.com",
        "123-456-7890"
    )

    print("\n=== Request Booking ===")
    res = dorm.request_booking(
        "RS-0002",
        "A01",
        RoomType.STANDARD_ROOM,
    )
    pprint(res)

    print("\n=== Sign Contract ===")
    res = dorm.sign_contract(
        "LC-0002"
    )
    pprint(res)

    print("\n=== Pay Contract Invoice ===")
    res = dorm.pay_contract_invoice(
        "INV-0002",
    )
    pprint(res)

    print("\n=== Complete Hand Over ===")
    res = dorm.complete_handover(
        "LC-0002"
    )
    pprint(res)

"""======================================="""

init_mock_data()

run_tests()

print_all_data()
