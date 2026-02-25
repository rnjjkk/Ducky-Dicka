from fastapi import FastAPI
import uvicorn
# from datetime import datetime
import datetime
import calendar
from pydantic import BaseModel

class Dorm:
    def __init__(self, name: str):
        self.__name = name
        self.__residents = []
        self.__rooms = []

    @property
    def residents(self):
        return self.__residents

    def add_resident(self, resi):
        self.__residents.append(resi)

    def add_room(self, room):
        self.__rooms.append(room)

    def search_resident_by_id(self, residentId):
        for resident in self.__residents:
            if int(resident.id[-4:]) == int(residentId):
                return resident
        return None

    def search_room_by_id(self, roomId):
        for room in self.__rooms:
            if room.id == roomId:
                return room
        return None

    def change_lease_contract(self, 
                            residentId,
                            currentLeaseContractId,
                            targetRoomId,
                            moveDate
                            ):
        # return self.search_resident_by_id(residentId)
        resident = self.search_resident_by_id(residentId)
        if resident is None:
            return {"response": "resident not found"}

        cur_contract = resident.search_contract_by_id(currentLeaseContractId)
        if cur_contract is None:
            return {"response": "current contract not found"}

        if cur_contract == "EXPIRED":
            return {"response": "expired contract not found"}

        target_room = self.search_room_by_id(targetRoomId)
        if target_room is None:
            return {"response": "target room not found"}

        if target_room.status != "AVAILABLE":
            return {"response": "target room not available"}

        if len(resident.invoices) > 0:
            return {"response": "reject"}

        invoice = cur_contract.calculate_upgrade_amount(target_room.ROOM_COST, moveDate)
        old_room = cur_contract.room
        old_room.status = "AVAILABLE"
        cur_contract.room = target_room
        target_room.status = "OCCUPIED"

        resident.add_invoice(invoice)
        return {"resident": resident,
                "old-room": old_room,
                }

class User:
    def __init__(self, id: str, name: str, email: str, phone_number: str):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__date__create = datetime.date.today()

    @property
    def id(self):
        return self.__id

class Resident(User):
    ID = 1
    
    def __init__(self, name: str, email: str, phone_number: str, status=None):
        super().__init__(f"RS-{datetime.date.year}-{Resident.ID:04d}", name, email, phone_number)
        self.__bookings: list = []
        self.__invoices: list = []
        self.__status = status

        Resident.ID += 1

    def add_booking(self, booking):
        self.__bookings.append(booking)

    def add_invoice(self, invoice):
        self.__invoices.append(invoice)

    def search_contract_by_id(self, contractId):
        for booking in self.__bookings:
            if int(booking.contract.id[-4:]) == int(contractId):
                return booking.contract
        return None

    @property
    def invoices(self):
        return self.__invoices

class Booking:
    ID = 1
    
    def __init__(self, id):
        self.__id = id
        self.__contract: object = None

        Booking.ID += 1

    @property
    def contract(self):
        return self.__contract

    def set_contract(self, contract):
        self.__contract = contract

class Contract:
    ID = 1
    
    def __init__(self, room, status=None):
        self.__id = f"LC-{datetime.date.today().year}{datetime.date.today().month}-{Contract.ID:04d}"
        self.__room = room
        self.__status = status

        Contract.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def room(self):
        return self.__room

    @room.setter
    def room(self, room):
        self.__room = room

    def calculate_upgrade_amount(self, target_room_cost, moveDate):
        move_date = datetime.datetime.strptime(moveDate, "%Y-%m-%d").date()
        days_in_month = calendar.monthrange(move_date.year, move_date.month)[1]

        days_left = days_in_month - move_date.day + 1
        print(days_left)
        avg_new_room_cost = target_room_cost / days_in_month
        print(avg_new_room_cost)
        new_room_cost = avg_new_room_cost * days_left
        print(new_room_cost)
        
        old_room_cost = (self.__room.ROOM_COST / days_in_month) * days_left
        print(old_room_cost)
        cost_diff = new_room_cost - old_room_cost

        return Invoice(round(cost_diff, 2))

class Room:
    def __init__(self,id: str, building: str, floor: str, status):
        self.__id = id
        self.__buidling = building
        self.__floor = floor
        self.__status = status

    @property
    def id(self):
        return self.__id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

class Standard_Room(Room):
    ID = 1
    ROOM_SIZE = 26
    ROOM_COST = 8200

    def __init__(self, building, floor, status=None):
        super().__init__(f"RM-STANDARD-{building}-{floor}-{Standard_Room.ID:04d}", building, floor, status)

        Standard_Room.ID += 1

class Studio_Room(Room):
    ID = 1
    ROOM_SIZE = 20
    ROOM_COST = 6500

    def __init__(self, building, floor, status=None):
        super().__init__(f"RM-STUDIO-{building}-{floor}-{Studio_Room.ID:04d}", building, floor, status)

        Studio_Room.ID += 1

class Invoice:
    def __init__(self, amount):
        self.amount = amount
        self.type = "CHARGE" if amount > 0 else "CREDIT"

"""==============================================================================="""

dorm = Dorm("DormiKa")

kenny = Resident("ken", "ken@gmail.com", "1234567890", "ACTIVE")
print(calendar.monthrange(2026, datetime.date.today().month)[1])
print(type(calendar.monthrange(2026, datetime.date.today().month)))
dorm.add_resident(kenny)

std_room = Standard_Room("A01", "05", "OCCUPIED")
sto_room = Studio_Room("A01", "02", "AVAILABLE")
print(sto_room.id)
dorm.add_room(std_room)
dorm.add_room(sto_room)

booking = Booking(f"BK-{datetime.date.today().strftime("%Y%m%d")}-{Booking.ID:04d}")
contract = Contract(std_room, "ACTIVE")

booking.set_contract(contract)
kenny.add_booking(booking)

"""==============================================================================="""

app = FastAPI()

class ChangeContractRequest(BaseModel):
    residentId: str
    currentLeaseContractId: str
    targetRoomId: str
    moveDate: str

"""
{
  "residentId": "1",
  "currentLeaseContractId": "1",
  "targetRoomId": "RM-STUDIO-A01-02-0001",
  "moveDate": "2026-2-27"
}
"""

@app.post("/change-contract")
async def change_lease_contract(request: ChangeContractRequest):
    return dorm.change_lease_contract(request.residentId,
                                      request.currentLeaseContractId,
                                      request.targetRoomId,
                                      request.moveDate
                                      )

if __name__ == "__main__":
    uvicorn.run("change_contract:app", host="127.0.0.1", port=8000, reload=True)