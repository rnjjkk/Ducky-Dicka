from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timedelta
import uvicorn


class AccountStatus(Enum):
    PENDING_VERIFICATION = "Pending Verification"
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    CLOSED = "Closed"

class LeaseStatus(Enum):
    DRAFT = "Draft"
    PENDING_SIGN = "Pending Sign"
    ACTIVE = "Active"
    EXPIRED = "Expired"

class RoomStatus(Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    OCCUPIED = "Occupied"
    MAINTENANCE = "Maintenance"


class User:
    def __init__(self, user_id, name, phone):
        self._user_id = user_id 
        self._name = name
        self._phone = phone

    @property
    def user_id(self):
        return self._user_id

class Resident(User):
    def __init__(self, user_id, name, phone, status=AccountStatus.PENDING_VERIFICATION):
        super().__init__(user_id, name, phone)
        self.status = status  

class Room:
    def __init__(self, room_type, building, floor, room_number, price): 
        # รูปแบบ ID: RM-[Type]-[อาคาร]-[ชั้น]-[หมายเลข] 
        self.room_id = f"RM-{room_type}-{building}-{floor}-{room_number}"
        self.price = price 
        self.status = RoomStatus.AVAILABLE
        self.hold_expiry = None

    def check_availability(self):
        return self.status == RoomStatus.AVAILABLE 

class Building:
    def __init__(self, building_id):
        self.building_id = building_id
        self.rooms = {}

    def add_room(self, room):
        self.rooms[room.room_id] = room

    def find_and_hold_room(self, room_id):
       
        room = self.rooms.get(room_id)
        if room and room.check_availability():
            room.status = RoomStatus.RESERVED
            room.hold_expiry = datetime.now() + timedelta(hours=48)
            return room
        return None

class LeaseContract:
    def __init__(self, contract_id, resident, room):
        self.contract_id = contract_id
        self.resident = resident
        self.room = room
        self.status = LeaseStatus.DRAFT 
        self.created_at = datetime.now()

class DormSystem:
    def __init__(self):
        self.users = []
        self.buildings = []
        self.contracts = []

    def get_user_by_id(self, user_id):
        
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def get_building_by_id(self, building_id):
        for b in self.buildings:
            if b.building_id == building_id:
                return b
        return None

app = FastAPI(title="Dorminika System")
system = DormSystem()

class BookingRequest(BaseModel):
    user_id: str
    building_id: str
    room_id: str  # ต้องส่งเป็น Full ID
@app.on_event("startup")
def startup_event():

    b1 = Building("A01")
    
    r1 = Room("Standard", "A01", "08", "0812", 6500)
    b1.add_room(r1)
    system.buildings.append(b1)
    
    u1 = Resident("U6801", "Tanawit", "081-XXX-XXXX", status=AccountStatus.ACTIVE)
    system.users.append(u1)

@app.post("/request_booking")
async def api_request_booking(req: BookingRequest):
    
    user = system.get_user_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found user_id")

   
    if user.status == AccountStatus.SUSPENDED:
        raise HTTPException(status_code=403, detail="Account restricted")

    
    current_hour = datetime.now().hour
    if not (8 <= current_hour <= 17):
        raise HTTPException(status_code=400, detail="Office hours not available")

   
    building = system.get_building_by_id(req.building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    
    room_obj = building.find_and_hold_room(req.room_id)
    if room_obj is None:
        raise HTTPException(status_code=400, detail="Room is busy or maintenance")

    
    contract_id = f"LC-{datetime.now().strftime('%Y%m')}-{len(system.contracts)+1:04d}"
    new_contract = LeaseContract(contract_id, user, room_obj)
    system.contracts.append(new_contract)

    return {
        "status": "success",
        "lease_id": new_contract.contract_id,
        "room_id": room_obj.room_id,
        "room_status": room_obj.status.value,
        "message": "Booking successful, held for 48 hours."
    }

if __name__ == "__main__":
   
    uvicorn.run("main3:app", host="127.0.0.1", port=8000, reload=True)