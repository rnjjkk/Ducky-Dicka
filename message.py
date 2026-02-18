from abc import ABC, abstractmethod
from datetime import datetime
from fastapi import FastAPI
import uvicorn

class Dorm : 
    def __init__(self, name):
        self.__name = name
        self.__building_list = []
        self.__user_list = []
        self.__resident_list = []
        self.__os_staff_list = []
        self.__system_admin_list = []
        self.__building_manager_list = []

    def verify_resident_by_id(self, resident_id):
        for resident in self.__resident_list:
            if int(resident.id[-4:]) == int(resident_id):
                return resident
        raise PermissionError("Resident_id not found")
        
    def payment(self, resident_id, paymentdata):
        try :
            resident_obj = self.verify_resident_by_id(resident_id)
        except PermissionError as e:
            print(f"✓ Expected Error: {e}")
            return self.showLoginError()
        
        try :
            payment_obj = resident_obj.getPayment()
        except ValueError as e:
            print(f"✓ Expected Error: {e}")
            return self.paymentFailed(str(e))

        # pay(paymentdata)
        try:
            payment_obj.pay(paymentdata)
        except ValueError as e:
            print(f"✓ Expected Error: {e}")
            return self.paymentFailed(str(e))

        # pay : success
        resident_obj.removeInvoice(payment_obj)

        # loop markPaid()
        for inv in payment_obj._Payment__invoices:
            inv.markPaid()

        # createReceipt(Payment, createAt)
        receipt_obj = Receipt(payment_obj)

        # addReceipt(receipt)
        resident_obj.addReceipt(receipt_obj)

        return self.paymentSuccess(receipt_obj)

    # ===== methods in sequence =====
    def showLoginError(self):
        return {"ok": False, "fn": "showLoginError()"}

    def paymentFailed(self, errorMessage):
        return {"ok": False, "fn": "paymentFailed(errorMessage)", "errorMessage": errorMessage}

    def paymentSuccess(self, receipt):
        return {"ok": True, "fn": "paymentSuccess(receipt)", "receipt": receipt}


class User(ABC) : 
    def __init__(self, name, email, phone_number, id=None):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__strike = 0 # ยังไม่ต้องทำ

    @property
    def id(self):
        return self.__id


class Resident(User): 
    def __init__(self, id, name, email, phone_number, move_in_date):
        super().__init__(name, email, phone_number, id)
        self.__move_in_date = move_in_date
        self.__booking = []
        self.__discount = []
        self.__invoice = []
        self.__payment = None # instance ของ Payment ทำหน้าที่เหมือนตระกร้าใช้ เสร็จแล้วเปลี่ยนเป็น None
        self.__receipt = []
        self.__status = None # ยังไม่ต้องทำ
    
    @property
    def payment(self):
        return self.__payment
    
    def getPayment(self):
        if self.__payment != None :
            return self.__payment
        else : 
            raise ValueError("Payment not found")

    # ===== methods in sequence =====
    def removeInvoice(self, payment_obj):
        paid_list = payment_obj._Payment__invoices
        new_list = []
        for inv in self.__invoice:
            if inv not in paid_list:
                new_list.append(inv)
        self.__invoice = new_list

    def addReceipt(self, receipt_obj):
        self.__receipt.append(receipt_obj)


class Payment : 
    def __init__(self, invoices, payment_method, discount=None):
        self.__id = None # สร้างเอง
        self.__invoices = invoices          
        self.__payment_method = payment_method # instance ของ Bank_Account หรือ Card
        self.__discount = discount # ยังไม่ต้องทำ
    
    # ===== method in sequence =====
    def pay(self, paymentdata):
        if self.__payment_method is None:
            raise ValueError("payment_method not found")
        if self.__invoices is None or len(self.__invoices) == 0:
            raise ValueError("invoice_list is empty")

        # gateway.pay() (ใน diagram ไม่โชว์ gateway ก็เลยให้ Payment จัดการเอง)
        return self.__payment_method.pay()


class Invoice : 
    def __init__( self,                   resident_info,            invoice_type,
                  room_cost=None,         electricity_cost=None,    water_cost=None,
                  parking_slot_cost=None, share_facility_cost=None, maintenance_cost=None,
                  invoice_code=None,      invoice_status=None ):

        self.__resident_info = resident_info
        self.__invoice_type = invoice_type

        self.__room_cost = room_cost
        self.__electricity_cost = electricity_cost
        self.__water_cost = water_cost
        self.__parking_slot_cost = parking_slot_cost
        self.__share_facility_cost = share_facility_cost
        self.__maintenance_cost = maintenance_cost

        self.__invoice_code = invoice_code
        self.__invoice_status = invoice_status

        self.__discount_cost = 0
        self.__amount_before_discount = 0
        self.__net_amount = 0

        self.__reference_code_from_payment_gateway = None
        self.__refund_adjust_reason = None
        self.__refund_adjust_approver = None
        self.__refund_adjust_amount = 0

        self.__payment_method = None
        self.__fine = 0

        self.__adjustment_history = []
        self.__history_of_payment_attempts = []
        self.__record_of_approvers_for_fine_waivers_refunds = []

    # ===== method in sequence =====
    def markPaid(self):
        self.__invoice_status = "PAID"

class PaymentGateway(ABC) : 
    
    @abstractmethod
    def pay(self):
        pass


class Bank_Account(PaymentGateway) : 
    def __init__(self, bank_id, refer, reference_id):
        self.__bank_id = bank_id
        self.__reference_id = reference_id

    def pay(self):
        # ให้มัน “รันได้จริง” แบบง่ายสุด
        if self.__reference_id is None or self.__reference_id == "":
            raise ValueError("bank transfer fail")
        return True


class Card(PaymentGateway) : 
    def __init__(self, card_id, cardholder_name, expitation_date, CVV_CVC):
        self.__card_id = card_id
        self.__cardholder_name = cardholder_name
        self.__expitation_date = expitation_date
        self.__CVV_CVC = CVV_CVC

    def pay(self):
        # ให้มัน “รันได้จริง” แบบง่ายสุด
        if self.__card_id is None or self.__card_id == "":
            raise ValueError("card pay fail")
        if self.__CVV_CVC is None or str(self.__CVV_CVC) == "":
            raise ValueError("card pay fail")
        return True


class Receipt : 
    def __init__(self, payment):
        self.__payment = payment
        self.__createAt = datetime.now()

# ================================

dorm_system = Dorm("University Dorm")

def setup_mock_data():
    res = Resident(
        id="66001001", 
        name="Student A", 
        email="student@mail.com", 
        phone_number="0812345678", 
        move_in_date="2024-06-01"
    )

    inv = Invoice(
        resident_info=res, 
        invoice_type="Room Rent", 
        room_cost=4500
    )

    bank_acct = Bank_Account(
        bank_id="KBANK", 
        refer="University Account", 
        reference_id="SLIP-999" 
    )

    payment_obj = Payment(invoices=[inv], payment_method=bank_acct)

    dorm_system._Dorm__resident_list.append(res)
    
    res._Resident__payment = payment_obj 
    res._Resident__invoice.append(inv)
    
    print(">>> System Ready. Test with Resident ID: '1001'")

setup_mock_data()

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/payment")
@app.post("/payment")
async def make_payment(resident_id, paymentdata):
    result = dorm_system.payment(resident_id, paymentdata)
    
    return {"res": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)











# app = FastAPI()

# @app.post("/payment")
# async def make_payment(request: PaymentRequest):
#     result = dorm_system.payment(request.resident_id, request.payment_data)
#     if not result["ok"]:
#         return result
        
#     return result

# if __name__ == "__main__":
#     uvicorn.run("message:app", host="127.0.0.1",port=8000, log_level="info", reload=True)