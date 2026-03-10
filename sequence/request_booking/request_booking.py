from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timedelta
from typing import List
import uvicorn


class RoomType(Enum):
    STUDIOROOM      = "StudioRoom"
    STANDARDROOM    = "StandardRoom"
    ONEBEDROOMROOM  = "OneBedRoomRoom"

class RoomPrice(Enum):
    STUDIOROOM      = 6700
    STANDARDROOM    = 9100
    ONEBEDROOMROOM  = 10500

class RoomStatus(Enum):
    AVAILABLE         = "Available"
    RESERVED          = "Reserved"
    OCCUPIED          = "Occupied"
    TURNOVER_CLEANING = "Turnover_Cleaning"
    MAINTENANCE       = "Maintenance"
    DISABLE           = "Disable"

class AccountStatus(Enum):
    PENDING_VERIFICATION = "Pending Verification"
    ACTIVE               = "Active"
    SUSPENDED            = "Suspended"
    CLOSED               = "Closed"

class ContractStatus(Enum):
    DRAFT        = "DRAFT"
    PENDING_SIGN = "PENDING_SIGN"
    ACTIVE       = "ACTIVE"
    ENDING_SOON  = "ENDING_SOON"
    TERMINATED   = "TERMINATED"
    EXPIRED      = "EXPIRED"


class User:
    def __init__(self, user_id: str, name: str, phone: str):
        self.__user_id = user_id
        self.__name    = name
        self.__phone   = phone

    @property
    def user_id(self):
        return self.__user_id

    @property
    def name(self):
        return self.__name

    @property
    def phone(self):
        return self.__phone


class Resident(User):
    def __init__(self, user_id: str, name: str, phone: str,
                status: AccountStatus = AccountStatus.ACTIVE):
        super().__init__(user_id, name, phone)
        self.__status = status

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: AccountStatus):
        self.__status = new_status


class Room:
    def __init__(self, room_type: RoomType, building_id: str,
                floor: str, room_number: str, price: int):
        self.__room_type  = room_type
        self.__room_id    = f"RM-{room_type.value}-{building_id}-{floor}-{room_number}"
        self.__price      = price
        self.__status     = RoomStatus.AVAILABLE
        self.__hold_expiry = None

    @property
    def room_type(self):
        return self.__room_type

    @property
    def room_id(self):
        return self.__room_id

    @property
    def price(self):
        return self.__price

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: RoomStatus):
        self.__status = new_status

    @property
    def hold_expiry(self):
        return self.__hold_expiry

    @hold_expiry.setter
    def hold_expiry(self, expiry_date: datetime):
        self.__hold_expiry = expiry_date

    def check_availability(self) -> bool:
        return self.__status == RoomStatus.AVAILABLE


class Building:
    def __init__(self, building_id: str, floor_count: int):
        self.__id          = building_id
        self.__floor_count = floor_count
        self.__rooms: List[Room] = []

    @property
    def building_id(self):
        return self.__id

    def add_room(self, room: Room):
        self.__rooms.append(room)

    def find_and_hold_available_room_by_type(self, room_type: RoomType) -> Room:
        for room in self.__rooms:
            if room.room_type == room_type and room.check_availability():
                room.status      = RoomStatus.RESERVED
                room.hold_expiry = datetime.now() + timedelta(hours=48)
                return room
        raise LookupError(f"ไม่พบห้องว่างประเภท {room_type.value} ในตึกนี้")


class Contract:
    ID = 1

    def __init__(self, resident, room, status=ContractStatus.DRAFT):
        self.__contract_id = f"LC-{Contract.ID:04d}"
        Contract.ID += 1
        self.__resident    = resident
        self.__room        = room
        self.__status      = status
        self.__created_at  = datetime.now()

    @property
    def contract_id(self):
        return self.__contract_id

    @property
    def resident(self):
        return self.__resident

    @property
    def room(self):
        return self.__room

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: ContractStatus):
        self.__status = new_status

    @property
    def created_at(self):
        return self.__created_at


class DormSystem:
    def __init__(self):
        self.__users:     List[User]          = []
        self.__buildings: List[Building]      = []
        self.__contracts: List[Contract] = []

    @property
    def users(self):
        return self.__users

    @property
    def buildings(self):
        return self.__buildings

    @property
    def contracts(self):
        return self.__contracts

    def get_user_by_id(self, user_id: str) -> User:
        for user in self.__users:
            if user.user_id == user_id:
                return user
        raise LookupError(f"ไม่พบรหัสผู้ใช้งาน: {user_id}")

    def get_building_by_id(self, building_id: str) -> Building:
        for b in self.__buildings:
            if b.building_id == building_id:
                return b
        raise LookupError(f"ไม่พบตึก: {building_id}")

    def request_booking(self, user_id: str, building_id: str,
                        room_type: RoomType) -> Contract:

        user = self.get_user_by_id(user_id)

        if not isinstance(user, Resident):
            raise PermissionError("ประเภทผู้ใช้งานไม่ถูกต้อง")

        if user.status == AccountStatus.SUSPENDED:
            raise PermissionError("บัญชีถูกระงับการใช้งาน")

        if user.status == AccountStatus.PENDING_VERIFICATION:
            raise PermissionError("บัญชีอยู่ระหว่างการตรวจสอบ")

        if not (8 <= datetime.now().hour <= 17):
            raise ValueError("ขณะนี้อยู่นอกเวลาทำการ (08:00-17:00)")

        building = self.get_building_by_id(building_id)
        room     = building.find_and_hold_available_room_by_type(room_type)

        contract_id  = f"LC-{datetime.now().strftime('%Y%m')}-{len(self.__contracts)+1:04d}"
        new_contract = Contract(user, room)
        self.__contracts.append(new_contract)

        return new_contract



app    = FastAPI(title="Dorminika Booking System")
system = DormSystem()


class BookingRequest(BaseModel):
    user_id:     str
    building_id: str
    room_type:   RoomType


@app.on_event("startup")
def startup_event():
    b1 = Building("A01", 8)
    b1.add_room(Room(RoomType.STANDARDROOM,   "A01", "08", "0812", RoomPrice.STANDARDROOM.value))
    b1.add_room(Room(RoomType.STUDIOROOM,     "A01", "08", "0815", RoomPrice.STUDIOROOM.value))
    b1.add_room(Room(RoomType.ONEBEDROOMROOM, "A01", "07", "0701", RoomPrice.ONEBEDROOMROOM.value))
    system.buildings.append(b1)

    system.users.append(Resident("U6801", "Tanawit", "081-XXX-XXXX"))


@app.post("/request_booking", tags=["Booking"])
async def api_request_booking(req: BookingRequest):
    try:
        contract = system.request_booking(req.user_id, req.building_id, req.room_type)
        return {
            "status":           "success",
            "lease_id":         contract.contract_id,
            "assigned_room_id": contract.room.room_id,
            "room_type":        contract.room.room_type.value,
            "room_status":      contract.room.status.value,
            "message":          "การจองสำเร็จ",
        }
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
