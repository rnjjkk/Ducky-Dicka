from models.dorm import Dorm
from models.resident import Resident
from models.building import Building
from models.room import Room
from models.contract import Contract
from models.employee import Employee
from models.staff import Cleaner, PlumbingTech, ElectricalTech, ACTech
from models.share_facility import WashingMachine, MeetingRoom

from models.enum import *
from pprint import pprint


def init_mock_data():
    global dorm
    dorm = Dorm("========== DormiKa ==========")
    print(dorm.name)

    # Add a building
    building = Building(floor_count=5, zone="A")
    dorm.add_building(building)
    print(f"Building ID: {building.id}\n")

    # Add rooms to the building
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

    # Add shared facilities
    building.add_meeting_room(MeetingRoom())
    building.add_washing_machine(WashingMachine())
    
    # Add residents
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

    # Add contract for the first resident 
    resident = dorm.residents[0]
    room = dorm.buildings[0].rooms[0]
    contract = Contract(resident, room)
    resident.add_contract(contract)
    room.status = RoomStatus.OCCUPIED
    print(f"\nAdded {contract.id} to {resident.id}")

    # Add employees
    names = ["Harry", "Sally", "Tom", "Lucy", "Mia", "Oscar"]
    for i in range(len(names)):
        employee = Employee(
            name=names[i],
        )
        dorm.add_employee(employee)
        print(f"Added Employee: {employee.name}".ljust(25), end="")
        print(f"{employee.id}")

    # Add cleaners
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

    # Add technicians
    names = ["Mike", "Sara", "Leo"]
    technicians = [
        ElectricalTech(
            name=names[i],
            phone_number=f"555-987-654{i}",
            capabilities=["Electrical"],
            schedule=None,
            current_task=None,
            status=AvailabilityStatus.AVAILABLE,
            certification_no=["Electrical License"],
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
                print(
                    f"  - Contract ID: {contract.id}, Room: {contract.room.id}, Status: {contract.status.value}")
                print(
                    f"  - Room ID: {contract.room.id}, Type: {contract.room.type.value}, Rent: {contract.room.monthly_rent}")

    print("\n=== All Employees ===")
    for employee in dorm.employees:
        print(f"{employee.id}: {employee.name}")

    print("\n=== All Cleaners ===")
    for cleaner in dorm.cleaners:
        print(f"{cleaner.id}: {cleaner.name} - {cleaner.phone_number}")

    print("\n=== All Technicians ===")
    for tech in dorm.technicians:
        print(f"{tech.id}: {tech.name} - {tech.phone_number} - Capabilities: {', '.join(tech.capabilities)}")

    print("\n=== All Buildings ===")
    for building in dorm.buildings:
        print(f"{building.id}: {building.id}")
        for room in building.rooms:
            print(
                f"  - Room ID: {room.id}, Type: {room.type.value}, Status: {room.status.value}, Rent: {room.monthly_rent}")

    print("\n=== All Shared Facilities ===")
    for building in dorm.buildings:
            for facility in building.washing_machines:
                print(f"  - ID: {facility.id}")
            for facility in building.meeting_rooms:
                print(f"  - ID: {facility.id}")

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
    dorm.sign_contract(
        "LC-0001"
    )

    print("\n=== Pay Contract Invoice ===")
    res = dorm.pay_contract_invoice(
        "INV-0002",
    )
    pprint(res)
    dorm.pay_contract_invoice(
        "INV-0003",
    )

    print("\n=== Complete Hand Over ===")
    res = dorm.complete_handover(
        "LC-0002"
    )
    pprint(res)

    print("\n=== Create Member ===")
    res = dorm.create_member(
        "RS-0001",
        "PLUS"
    )
    pprint(res)

    print("\n=== Request Maintenance ===")
    res = dorm.request_maintenance(
        "RS-0001",
        "RM-0001",
        "Electrical",
    )
    pprint(res)

    print("\n=== Start Maintenance ===")
    res = dorm.start_maintenance_workflow(
        "TC-0001",
        "Fix wiring",
    )
    pprint(res)

    print("\n=== Finish Maintenance ===")
    res = dorm.finish_maintenance_workflow(
        "TC-0001",
    )
    pprint(res)


    print("\n=== Request Cleaning ===")
    res = dorm.request_cleaning_room(
        "RS-0001",
        "RM-0001",
    )
    pprint(res)

    print("\n=== Start Cleaning ===")
    res = dorm.start_cleaning_workflow(
        "CL-0001",
        "RM-0001",
    )
    pprint(res)

    print("\n=== Finish Cleaning ===")
    res = dorm.finish_cleaning_workflow(
        "CL-0001",
        "RM-0001",
    )
    pprint(res)

    print("\n=== Booking Share Facility ===")
    res = dorm.booking_share_facility(
        "RS-0001",
        "SHARE-0001",
        "A01",
        "2024-10-01 19:00"
    )
    pprint(res)

    print("\n=== Display Invoices ===")
    res = dorm.display_invoice(
        "RS-0001",
    )
    pprint(res)

    print("\n=== Select Payment ===")
    res = dorm.select_payment_method_and_invoices(
        "RS-0001",
        "Card",
        "INV-0004",
    )
    dorm.select_payment_method_and_invoices(
        "RS-0001",
        "Card",
        "INV-0001",
    )
    dorm.select_payment_method_and_invoices(
        "RS-0001",
        "Card",
        "INV-0007",
    )
    pprint(res)

    print("\n=== Pay ===")
    res = dorm.payment_system(
        "RS-0001",
        "666777, Kenny, 12/27, 123"
    )
    pprint(res)

    print("\n=== Display Receipt ===")
    res = dorm.display_receipt(
        "RS-0001",
    )

    print("\n=== Change Contract ===")
    res = dorm.change_contract(
        "RS-0001",
        "LC-0001",
        "RM-0005",
        "2024-10-01"
    )
    pprint(res)

    print("\n=== Add Strike ===")
    res = dorm.add_strike("EM-0001")
    pprint(res)

"""======================================="""

init_mock_data()
print("#####################################################")
print_all_data()
print("#####################################################")
run_tests()
