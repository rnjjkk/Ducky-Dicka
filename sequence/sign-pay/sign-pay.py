from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from enum import Enum
from datetime import datetime, timedelta
from typing import List
import uvicorn


class RoomType(Enum):
    STUDIO_ROOM    = "StudioRoom"
    STANDARD_ROOM  = "StandardRoom"
    ONE_BED_ROOM   = "OneBedRoomRoom"

class RoomPrice(Enum):
    STUDIO_ROOM    = 6700
    STANDARD_ROOM  = 9100
    ONE_BED_ROOM   = 10500

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

class InvoiceType(Enum):
    CONTRACT       = "invoice_contract"
    MAINTENANCE    = "invoice_maintenance"
    CLEANER        = "invoice_cleaner"
    MEMBER         = "invoice_member"
    SHARE_FACILITY = "invoice_share_facility"

class InvoiceStatus(Enum):
    PAID   = "paid"
    UNPAID = "unpaid"



class Resident:
    def __init__(self, resident_id: str, name: str, phone: str,
                status: AccountStatus = AccountStatus.ACTIVE):
        self.__resident_id = resident_id
        self.__name        = name
        self.__phone       = phone
        self.__status      = status

    @property
    def resident_id(self):
        return self.__resident_id

    @property
    def name(self):
        return self.__name

    @property
    def phone(self):
        return self.__phone

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: AccountStatus):
        self.__status = new_status


class Room:
    def __init__(self, room_type: RoomType, building_id: str,
                floor: str, room_number: str):
        self.__room_type   = room_type
        self.__room_id     = f"RM-{room_type.value}-{building_id}-{floor}-{room_number}"
        self.__price       = RoomPrice[room_type.name].value
        self.__status      = RoomStatus.AVAILABLE
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


class Invoice:
    ID = 1

    def __init__(self, amount: int, invoice_type: InvoiceType):
        self.__invoice_id   = f"INV-{Invoice.ID:04d}"
        self.__amount       = amount
        self.__invoice_type = invoice_type
        self.__status       = InvoiceStatus.UNPAID
        self.__created_at   = datetime.now()

        Invoice.ID += 1

    @property
    def invoice_id(self):
        return self.__invoice_id

    @property
    def amount(self):
        return self.__amount

    @property
    def invoice_type(self):
        return self.__invoice_type

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: InvoiceStatus):
        self.__status = new_status

    @property
    def created_at(self):
        return self.__created_at

    def validate_for_payment(self):
        if self.__status == InvoiceStatus.PAID:
            raise ValueError(f"Invoice {self.__invoice_id} ชำระเงินแล้ว")


class Contract:
    ID = 1

    def __init__(self, resident: Resident, room: Room,
                status: ContractStatus = ContractStatus.DRAFT):
        self.__contract_id = f"LC-{Contract.ID:04d}"
        self.__resident    = resident
        self.__room        = room
        self.__status      = status
        self.__invoice_id  = None
        self.__created_at  = datetime.now()

        Contract.ID += 1

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
    def invoice_id(self):
        return self.__invoice_id

    @invoice_id.setter
    def invoice_id(self, inv_id: str):
        self.__invoice_id = inv_id

    @property
    def created_at(self):
        return self.__created_at

    def get_amount(self) -> int:
        return self.__room.price

    def validate_for_signing(self):
        if self.__status != ContractStatus.DRAFT:
            raise ValueError(
                f"สัญญา {self.__contract_id} ไม่สามารถ sign ได้ "
                f"(สถานะปัจจุบัน: {self.__status.value} — ต้องเป็น DRAFT เท่านั้น)"
            )


class DormSystem:
    def __init__(self):
        self.__residents: List[Resident]      = []
        self.__buildings: List[Building]      = []
        self.__contracts: List[Contract] = []
        self.__invoices:  List[Invoice]       = []

    @property
    def residents(self):
        return self.__residents

    @property
    def buildings(self):
        return self.__buildings

    @property
    def contracts(self):
        return self.__contracts

    @property
    def invoices(self):
        return self.__invoices

    def get_resident_by_id(self, resident_id: str) -> Resident:
        for resident in self.__residents:
            if resident.resident_id == resident_id:
                return resident
        raise LookupError(f"ไม่พบรหัสผู้พัก: {resident_id}")

    def get_building_by_id(self, building_id: str) -> Building:
        for b in self.__buildings:
            if b.building_id == building_id:
                return b
        raise LookupError(f"ไม่พบตึก: {building_id}")

    def get_contract_by_id(self, contract_id: str) -> Contract:
        for c in self.__contracts:
            if c.contract_id == contract_id:
                return c
        raise LookupError(f"ไม่พบสัญญา: {contract_id}")

    def get_invoice_by_id(self, invoice_id: str) -> Invoice:
        for i in self.__invoices:
            if i.invoice_id == invoice_id:
                return i
        raise LookupError(f"ไม่พบ invoice: {invoice_id}")

    def pay_invoice(self, invoice_id: str) -> Contract:
        # 1. หา invoice
        invoice = self.get_invoice_by_id(invoice_id)

        # 2. เช็คว่ายังไม่ได้จ่าย
        invoice.validate_for_payment()

        # 3. หา contract ที่ผูกกับ invoice นี้
        contract = next(
            (c for c in self.__contracts if c.invoice_id == invoice_id), None
        )
        if contract is None:
            raise LookupError(f"ไม่พบสัญญาที่ผูกกับ invoice: {invoice_id}")

        # 4. อัปเดต status
        invoice.status  = InvoiceStatus.PAID
        contract.status = ContractStatus.ACTIVE

        return contract

    def request_booking(self, resident_id: str, building_id: str,
                        room_type: RoomType) -> Contract:
        # 1. ตรวจสอบ resident
        resident = self.get_resident_by_id(resident_id)

        if resident.status == AccountStatus.SUSPENDED:
            raise PermissionError("บัญชีถูกระงับการใช้งาน")

        if resident.status == AccountStatus.PENDING_VERIFICATION:
            raise PermissionError("บัญชีอยู่ระหว่างการตรวจสอบ")

        # 2. ตรวจสอบเวลาทำการ
        if not (8 <= datetime.now().hour <= 17):
            raise ValueError("ขณะนี้อยู่นอกเวลาทำการ (08:00–17:00)")

        # 3. หาตึกและห้องว่าง
        building = self.get_building_by_id(building_id)
        room     = building.find_and_hold_available_room_by_type(room_type)

        # 4. สร้างสัญญา (ID auto-generate จาก class counter)
        new_contract = Contract(resident, room)
        self.__contracts.append(new_contract)

        return new_contract

    def sign_contract(self, contract_id: str) -> Invoice:
        # 1. หาสัญญา
        contract = self.get_contract_by_id(contract_id)

        # 2. ตรวจสอบ status ต้องเป็น DRAFT เท่านั้น
        contract.validate_for_signing()

        # 3. สร้าง invoice โดยดึง amount จาก contract -> room
        invoice = Invoice(contract.get_amount(), InvoiceType.CONTRACT)
        self.__invoices.append(invoice)

        # 4. ผูก invoice_id ไว้ใน contract และอัปเดต status
        contract.invoice_id = invoice.invoice_id
        contract.status     = ContractStatus.PENDING_SIGN

        return invoice


# ── FastAPI App ───────────────────────────────────────────────────────────────

app    = FastAPI(title="Dorminika Booking System")
system = DormSystem()


class BookingRequest(BaseModel):
    resident_id: str  = Field(..., example="U6801")
    building_id: str  = Field(..., example="A01")
    room_type:   RoomType  = Field(..., example="StandardRoom")

class SignContractRequest(BaseModel):
    contract_id: str  = Field(..., example="LC-0001")

class PayRequest(BaseModel):
    invoice_id: str


@app.on_event("startup")
def startup_event():
    b1 = Building("A01", 8)
    b1.add_room(Room(RoomType.STANDARD_ROOM,   "A01", "08", "0812"))
    b1.add_room(Room(RoomType.STUDIO_ROOM,     "A01", "08", "0815"))
    b1.add_room(Room(RoomType.ONE_BED_ROOM,    "A01", "07", "0701"))
    system.buildings.append(b1)

    system.residents.append(Resident("U6801", "Tanawit", "081-XXX-XXXX"))


@app.post("/request_booking", tags=["Booking"])
async def api_request_booking(req: BookingRequest):
    try:
        contract = system.request_booking(req.resident_id, req.building_id, req.room_type)
        return {
            "status":           "success",
            "contract_id":      contract.contract_id,
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


@app.post("/sign_contract", tags=["Booking"])
async def api_sign_contract(req: SignContractRequest):
    try:
        invoice = system.sign_contract(req.contract_id)
        return {
            "status":       "success",
            "invoice_id":   invoice.invoice_id,
            "amount":       invoice.amount,
            "invoice_type": invoice.invoice_type.value,
            "message":      "สร้าง invoice สำเร็จ กรุณาชำระเงินภายในกำหนด",
        }
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")


@app.post("/pay", tags=["Booking"])
async def api_pay(req: PayRequest):
    try:
        contract = system.pay_invoice(req.invoice_id)
        return {
            "status":      "success",
            "contract_id": contract.contract_id,
            "contract_status": contract.status.value,
            "message":     "ชำระเงินสำเร็จ สัญญามีผลแล้ว",
        }
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบ")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)