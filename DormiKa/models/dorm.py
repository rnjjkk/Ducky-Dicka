from .contract import *
from .room import *
from .resident import *
class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technicians: list = []
        self.__cleaner: list = []

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, employee):
        self.__employees.append(employee)

    def add_technician(self, technician):
        self.__technicians.append(technician)

    def add_building(self, building):
        self.__buildings.append(building)

    def search_resident_by_id(self, resident_id):
        for resident in self.__residents:
            if resident.id == resident_id:
                return resident
        return None

    def search_room_by_id(self, room_id):
        for building in self.__buildings:
            for room in building.rooms:
                if room.id == room_id:
                    return room
        return None
    
    def search_room_by_contract(self,room_id):
        pass

    def search_available_employee(self):
        for employee in self.__employees:
            if employee.status == "AVAILABLE":
                return employee
        return None

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

        if target_room.status != RoomStatus.Available:
            return {"response": "target room not available"}

        if len(resident.invoices) > 0:
            return {"response": "please settle existing invoices before changing contract"}

        invoice = current_contract.calculate_upgrade_amount(target_room.ROOM_COST, moveDate)
        old_room = current_contract.room
        old_room.status = RoomStatus.Available
        current_contract.room = target_room
        target_room.status = RoomStatus.Occupied

        resident.add_invoice(invoice)
        return {"resident": resident,
                "old-room": old_room,
                }
    
    def request_cleaning_room(self,resident_id,room_id):
        # resident input resident_id and search_resident_by_id to get resident instance
        resident = self.search_resident_by_id(resident_id)

        # resident input roomt_id and search_room_by_id to get room instance
        room_input = self.search_room_by_id(room_id)

        # get contract_list from resident
        contract_list = resident.contracts

        # search room in contracts
        room_in_contract = self.search_room_by_id()

