from .contract import *
from .room import *
from .resident import *
from unittest.mock import MagicMock
class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technicians: list = []
        self.__cleaner: list = []

    def show_success(self, success):
        print(success)
        return success

    def show_error(self, error):
        print(error)
        return error

    def add_employee(self, employee):
        self.__employees.append(employee)

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, employee):
        self.__employees.append(employee)

    def add_technician(self, technician):
        self.__technicians.append(technician)

    def add_building(self, building):
        self.__buildings.append(building)

    def search_employee_by_id(self, employee_id):
        for employee in self.__employees :
            if employee.id == employee_id:
                return employee
        raise PermissionError("Employee id : not found")
    
    def search_resident_by_id(self, resident_id):
        for resident in self.__residents:
            if resident.id == resident_id:
                return resident
        raise PermissionError("Resident id : not found")

    def search_room_by_id(self, room_id):
        for building in self.__buildings:
            for room in building.rooms:
                if room.id == room_id:
                    return room
        raise PermissionError("Room id : not found")
    
    def search_room_by_contracts(self,resident,room_id):
        for contract in resident.contracts:
            if contract.room.room.id == room_id:
                return contract.room
        raise ValueError("request wrong room resident doesn't in contract")

    def search_available_employee(self):
        for employee in self.__employees:
            if employee.status == "AVAILABLE":
                return employee
        raise ValueError("No employee are available at the moment")
    
    def request_cleaning_room(self,resident_id,room_id):
        # 1.search resident by id
        resident = self.search_resident_by_id(resident_id)

        # 2. serach room by id (room resident input)
        room_input = self.search_room_by_id(room_id)

        # 3. search room by contracts (room in resident contract)
        room_in_contract = self.search_room_by_contracts(resident,room_input.id)

        # 4. get cleaning ticket list
        cleaning_ticket_list = room_in_contract.cleaning_tickets

        # 5. check status cleaning ticket
        try:
            if resident.check_status_cleaning_ticket(cleaning_ticket_list):
                # 6. create cleaning ticket
                cleaning_ticket = resident.create_cleaning_ticket(resident_id, room_id)
                # 7. add cleaning ticket to room
                resident.add_cleaning_ticket(room_in_contract, cleaning_ticket)
                # 8. request success
                s = {
                    "reporter": resident.name,
                    "room_id": cleaning_ticket.room_id,
                    "ticket id": cleaning_ticket.id,
                    "report_time": cleaning_ticket.report_time,
                    "cost": cleaning_ticket.cost,
                    "status": cleaning_ticket.status
                }
                return self.show_success(s)
            else:
                return self.show_error({"error": "Cleaning ticket already exists or invalid status"})

        except Exception as e:
            return self.show_error({"error": str(e)})
    
    def request_maintenance(self, resident_id, room_id, issue_category):
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return {"error": "resident not found!"}

        room = self.search_room_by_id(room_id)
        if room is None:
            return {"error": "room not found!"}

        employee = self.search_available_employee()
        if employee is None:
            return {"error": "no available staff!"}
        
        return employee.start_maintenance(
            resident, 
            self.__technicians,
            room,
            issue_category
        )

    def system_contract_invoice(self, employee_ID_input):
        employee = self.search_employee_by_id(employee_ID_input)
        for resident in self.__residents:
            for contract in resident.contracts:
                monthly_rent = contract.room.monthly_rent
                room_id = contract.room.id
                invoice = employee.create_contract_invoice(monthly_rent, room_id)
                resident.add_invoice(invoice)
        s = 'system_contract_invoice : success'
        self.show_success(s)

    def select_payment_method_and_invoices(self, Resident_ID_input, payment_method_input, invoice_ids):
        resident = self.search_resident_by_id(Resident_ID_input)
        payment = resident.set_payment(payment_method_input, invoice_ids)
        format = payment.payment_method.payment_format()
        net_amount = payment.net_amount
        s = f'select_payment_method_and_invoices : success\nAmount to be paid : {net_amount}\n{format}'
        self.show_success(s)

    def payment_system(self, Resident_ID_input, paymentdata):
        resident = self.search_resident_by_id(Resident_ID_input)
        receipt = resident.payment(paymentdata)
        receipt_id = receipt.id
        s = f'payment_system : success\nreceipt : {receipt_id}'
        self.show_success(s)

    def change_contract(self, 
                            residentId,
                            currentLeaseContractId,
                            targetRoomId,
                            moveDate
                            ):
        resident = self.search_resident_by_id(residentId)
        if resident is None:
            return {"response": "resident not found"}

        current_contract = resident.search_contract_by_id(currentLeaseContractId)
        if current_contract is None:
            return {"response": "current contract not found"}

        if current_contract.status == ContractStatus.EXPIRED:
            return {"response": "expired contract not found"}

        target_room = self.search_room_by_id(targetRoomId)
        if target_room is None:
            return {"response": "target room not found"}

        if target_room.status != RoomStatus.AVAILABLE:
            print(target_room.status, RoomStatus.AVAILABLE)
            return {"response": "target room not available"}

        if len(resident.invoices) > 0:
            return {"response": "please settle existing invoices before changing contract"}

        invoice = current_contract.calculate_upgrade_amount(target_room.rental, moveDate)
        old_room = current_contract.room
        old_room.status = RoomStatus.AVAILABLE
        current_contract.room = target_room
        target_room.status = RoomStatus.OCCUPIED

        resident.add_invoice(invoice)
        return {
            "resident": {
                "id": resident.id,
                "status": resident.status,
                "new_room": target_room.id,
                "invoice": {
                    "id": invoice.id,
                    "amount": invoice.amount,
                } if invoice else None,
            },
            "old-room": {
                "id": old_room.id,
                "status": old_room.status.value,
            }
        }
    
    def display_invoice(self, resident_id_input):
        resident = self.search_resident_by_id(resident_id_input)
        for invoice in resident.invoices :
            print(invoice.id)
        s = f'display_invoice : success'
        self.show_success(s)

    def display_receipt(self, resident_id_input):
        resident = self.search_resident_by_id(resident_id_input)
        for receipt in resident.receipts:
            print(receipt.id)
        s = f'display_receipt : success'
        self.show_success(s)


def run_test(name, dorm):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"{'='*50}")
    try:
        result = request_cleaning_room(dorm, "RES001", "R101")
        print(f"RESULT: {result}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

# -------------------------------------------------------
# function จริงที่ test
# -------------------------------------------------------
def request_cleaning_room(self, resident_id, room_id):
    resident = self.search_resident_by_id(resident_id)
    room_input = self.search_room_by_id(room_id)
    room_in_contract = self.search_room_by_contracts(resident, room_input.id)
    cleaning_ticket_list = room_in_contract.cleaning_tickets

    try:
        if resident.check_status_cleaning_ticket(cleaning_ticket_list):
            cleaning_ticket = resident.create_cleaning_ticket(resident_id, room_id)
            resident.add_cleaning_ticket(room_in_contract, cleaning_ticket)
            s = {
                "reporter": resident.name,
                "room_id": cleaning_ticket.room_id,
                "ticket id": cleaning_ticket.id,
                "report_time": cleaning_ticket.report_time,
                "cost": cleaning_ticket.cost,
                "status": cleaning_ticket.status
            }
            return self.show_success(s)
        else:
            return self.show_error({"error": "Cleaning ticket already exists or invalid status"})
    except Exception as e:
        return self.show_error({"error": str(e)})

# -------------------------------------------------------
# helper สร้าง mock พื้นฐาน
# -------------------------------------------------------
def base_mock():
    dorm = MagicMock()

    resident = MagicMock()
    resident.name = "John Doe"

    room_input = MagicMock()
    room_input.id = "R101"

    room_in_contract = MagicMock()
    room_in_contract.cleaning_tickets = []

    cleaning_ticket = MagicMock()
    cleaning_ticket.room_id = "R101"
    cleaning_ticket.id = "CT001"
    cleaning_ticket.report_time = "2024-01-01 10:00"
    cleaning_ticket.cost = 100
    cleaning_ticket.status = "pending"

    dorm.search_resident_by_id.return_value = resident
    dorm.search_room_by_id.return_value = room_input
    dorm.search_room_by_contracts.return_value = room_in_contract
    dorm.show_success.side_effect = lambda s: {"success": True, "data": s}
    dorm.show_error.side_effect = lambda e: {"success": False, "data": e}

    resident.check_status_cleaning_ticket.return_value = True
    resident.create_cleaning_ticket.return_value = cleaning_ticket

    return dorm, resident, room_in_contract, cleaning_ticket

# -------------------------------------------------------
# case 1: success
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
run_test("Case 1: Success", dorm)

# -------------------------------------------------------
# case 2: check_status return False
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
resident.check_status_cleaning_ticket.return_value = False
run_test("Case 2: Already has ticket", dorm)

# -------------------------------------------------------
# case 3: resident not found
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
dorm.search_resident_by_id.side_effect = Exception("Resident not found")
run_test("Case 3: Resident not found", dorm)

# -------------------------------------------------------
# case 4: room not found
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
dorm.search_room_by_id.side_effect = Exception("Room not found")
run_test("Case 4: Room not found", dorm)

# -------------------------------------------------------
# case 5: room not in contract
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
dorm.search_room_by_contracts.side_effect = Exception("Room not in contract")
run_test("Case 5: Room not in contract", dorm)

# -------------------------------------------------------
# case 6: create_cleaning_ticket fails
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
resident.create_cleaning_ticket.side_effect = Exception("Failed to create ticket")
run_test("Case 6: Create ticket fails", dorm)

# -------------------------------------------------------
# case 7: add_cleaning_ticket fails
# -------------------------------------------------------
dorm, resident, room_in_contract, cleaning_ticket = base_mock()
resident.add_cleaning_ticket.side_effect = Exception("Failed to add ticket")
run_test("Case 7: Add ticket fails", dorm)