from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import datetime
import uvicorn


class RoomStatus(Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    OCCUPIED = "Occupied"
    TURNOVER_CLEANING = "Turnover_Cleaning"
    MAINTENANCE = "Maintenance"
    DISABLE = "Disable"

class ContractStatus(Enum):
    DRAFT = "DRAFT"
    PENDING_SIGN = "PENDING_SIGN"
    ACTIVE = "ACTIVE"
    ENDING_SOON = "ENDING_SOON"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"



class Building:
    def __init__(self, building_id):
        self.__id = building_id
    
    @property
    def id(self):
        return self.__id


class Room:
    def __init__(self, room_id, building_obj: Building, floor: int):
        self.__room_id = room_id  
        self.__building = building_obj
        self.__floor = floor
        self.__status = RoomStatus.AVAILABLE

    def fid(self):
        
        return f"RM-{self.__building.id}-{self.__floor:02d}-{self.__room_id[-4:]}"

    @property
    def room_id(self):
        return self.__room_id

    def record_handover(self):
        if self.__status != RoomStatus.AVAILABLE:
            raise ValueError(f"ห้อง {self.fid()} ไม่พร้อมส่งมอบ (สถานะปัจจุบัน: {self.__status.value})")
        
        self.__status = RoomStatus.OCCUPIED
        return True

class Contract:
    def __init__(self, contract_id, room_obj: Room):
        self.__contract_id = contract_id
        self.__room = room_obj
        self.__status = ContractStatus.PENDING_SIGN

    @property
    def id(self):
        return self.__contract_id

    def validate_contract_status_for_handover(self):
        valid_statuses = [ContractStatus.ACTIVE, ContractStatus.PENDING_SIGN]
        if self.__status not in valid_statuses:
            raise ValueError(f"สัญญา {self.__contract_id} มีสถานะไม่ถูกต้อง ({self.__status.value})")
        return True

    def get_room(self):
        return self.__room

class Resident:
    def __init__(self, resident_id: int, name: str, date_create: datetime = None):
        self.__id = resident_id  
        self.__name = name
        self.__date_create = date_create if date_create else datetime.now()
        self.__contracts: List[Contract] = []

    def fid(self):
        return f"RS-{self.__date_create.year}-{self.__id:04d}"

    def add_contract(self, contract: Contract):
        self.__contracts.append(contract)

    #   ตรวจสอบว่าผู้พักคนนี้มีสัญญาที่ตรงกับ contract_id หรือไม่ ตรง find_resident_by_contract
    def has_contract(self, contract_id):
        for each_contract in self.__contracts:
            if each_contract.id == contract_id:
                return True 
        return False 
    
    def get_contract(self, contract_id):
        for c in self.__contracts:
            if c.id == contract_id: 
                return c
        raise KeyError(f"ไม่พบสัญญา ID: {contract_id} ในรายชื่อของผู้พักคนนี้")

class Dorm:
    def __init__(self):
        self.__resident_list: List[Resident] = []

    def add_resident(self, resident: Resident):
        self.__resident_list.append(resident)
    
    def find_resident_by_contract(self, contract_id):
        for resident in self.__resident_list:
            if resident.has_contract(contract_id):
                return resident
        raise LookupError(f"ไม่พบผู้พักที่ถือครองสัญญา ID: {contract_id}")

    def complete_handover(self, contract_id: str):

        resident = self.find_resident_by_contract(contract_id)
        
        contract_obj = resident.get_contract(contract_id)

        contract_obj.validate_contract_status_for_handover()

        room_obj = contract_obj.get_room()
        room_obj.record_handover()
        

        return f"ดำเนินการส่งมอบสำเร็จ | สัญญา: {contract_id} | ห้อง: {room_obj.fid()} | ผู้พัก: {resident.fid()}"


app = FastAPI(title="ระบบจัดการการส่งมอบห้องพัก")
my_dorm = Dorm()

building_a = Building("A")

mock_room = Room("ROOM-101", building_a, 1)

mock_contract = Contract("CON-2024-X", mock_room)

mock_resident = Resident(777, "Harry Potter", datetime(2024, 5, 20))
mock_resident.add_contract(mock_contract)

my_dorm.add_resident(mock_resident)

class HandoverRequest(BaseModel):
    contract_id: str

@app.post("/handover", tags=["Dorm Services"])
async def process_handover(request: HandoverRequest):
    try:
        msg = my_dorm.complete_handover(request.contract_id)
        return {"status": "success", "message": msg}
    except (LookupError, KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)