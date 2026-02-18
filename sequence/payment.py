from abc import ABC, abstractmethod
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# ==========================================
#               CLASS ZONE
# ==========================================

class Dorm: 
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
            # FIX: Use string comparison to be safe (avoid int conversion errors)
            if str(resident.id)[-4:] == str(resident_id):
                return resident
        raise PermissionError("Resident_id not found")
        
    def payment(self, resident_id, paymentdata):
        try:
            resident_obj = self.verify_resident_by_id(resident_id)
        except PermissionError as e:
            return self.showLoginError()
        
        try:
            payment_obj = resident_obj.getPayment()
        except ValueError as e:
            return self.paymentFailed(str(e))

        try:
            payment_obj.pay(paymentdata)
        except ValueError as e:
            return self.paymentFailed(str(e))

        resident_obj.removeInvoice(payment_obj)

        for inv in payment_obj._Payment__invoices:
            inv.markPaid()

        receipt_obj = Receipt(payment_obj)
        resident_obj.addReceipt(receipt_obj)

        return self.paymentSuccess(receipt_obj)

    # ===== methods in sequence =====
    def showLoginError(self):
        return {"ok": False, "fn": "showLoginError()"}

    def paymentFailed(self, errorMessage):
        return {"ok": False, "fn": "paymentFailed(errorMessage)", "errorMessage": errorMessage}

    def paymentSuccess(self, receipt):
        # FIX: Do NOT return the 'receipt' object directly. 
        # FastAPI cannot turn a Class Object into JSON. Return a string or dict instead.
        return {
            "ok": True, 
            "fn": "paymentSuccess(receipt)", 
            "receipt_info": "Payment Successful. Receipt Created." 
        }


class User(ABC): 
    def __init__(self, name, email, phone_number, id=None):
        self.__id = id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__strike = 0

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
        self.__payment = None
        self.__receipt = []
        self.__status = None
    
    @property
    def payment(self):
        return self.__payment
    
    def getPayment(self):
        if self.__payment is not None:
            return self.__payment
        else: 
            raise ValueError("Payment not found (Cart is empty)")

    def removeInvoice(self, payment_obj):
        paid_list = payment_obj._Payment__invoices
        new_list = []
        for inv in self.__invoice:
            if inv not in paid_list:
                new_list.append(inv)
        self.__invoice = new_list

    def addReceipt(self, receipt_obj):
        self.__receipt.append(receipt_obj)


class Payment: 
    def __init__(self, invoices, payment_method, discount=None):
        self.__id = None
        self.__invoices = invoices          
        self.__payment_method = payment_method
        self.__discount = discount
    
    def pay(self, paymentdata):
        if self.__payment_method is None:
            raise ValueError("payment_method not found")
        if self.__invoices is None or len(self.__invoices) == 0:
            raise ValueError("invoice_list is empty")
        return self.__payment_method.pay()


class Invoice: 
    def __init__(self, resident_info, invoice_type,
                 room_cost=None, electricity_cost=None, water_cost=None,
                 parking_slot_cost=None, share_facility_cost=None, maintenance_cost=None,
                 invoice_code=None, invoice_status=None):

        self.__resident_info = resident_info
        self.__invoice_type = invoice_type
        self.__room_cost = room_cost
        self.__invoice_status = invoice_status
        # (Other fields omitted for brevity, keeping logic intact)

    def markPaid(self):
        self.__invoice_status = "PAID"


class PaymentGateway(ABC): 
    @abstractmethod
    def pay(self):
        pass


class Bank_Account(PaymentGateway): 
    def __init__(self, bank_id, refer, reference_id):
        self.__bank_id = bank_id
        self.__reference_id = reference_id

    def pay(self):
        if self.__reference_id is None or self.__reference_id == "":
            raise ValueError("bank transfer fail")
        return True


class Card(PaymentGateway): 
    def __init__(self, card_id, cardholder_name, expitation_date, CVV_CVC):
        self.__card_id = card_id
        self.__cardholder_name = cardholder_name
        self.__expitation_date = expitation_date
        self.__CVV_CVC = CVV_CVC

    def pay(self):
        if self.__card_id is None or self.__card_id == "":
            raise ValueError("card pay fail")
        if self.__CVV_CVC is None or str(self.__CVV_CVC) == "":
            raise ValueError("card pay fail")
        return True


class Receipt: 
    def __init__(self, payment):
        self.__payment = payment
        self.__createAt = datetime.now()


# ==========================================
#               MOCK DATA
# ==========================================
dorm_system = Dorm("University Dorm")

def setup_mock_data():
    res = Resident("66001001", "Student A", "student@mail.com", "0812345678", "2024-06-01")
    inv = Invoice(resident_info=res, invoice_type="Room Rent", room_cost=4500)
    bank_acct = Bank_Account("KBANK", "Uni Account", "SLIP-999")
    
    # Create Payment (Cart)
    payment_obj = Payment(invoices=[inv], payment_method=bank_acct)

    # Inject Data
    dorm_system._Dorm__resident_list.append(res)
    res._Resident__payment = payment_obj 
    res._Resident__invoice.append(inv)
    
    print(">>> System Ready. Test with Resident ID: '1001'")

setup_mock_data()


# ==========================================
#               API ZONE
# ==========================================
app = FastAPI()

# Input Model ensures parameters are read from JSON Body correctly
class PaymentRequest(BaseModel):
    resident_id: str
    paymentdata: str

@app.get("/payment")
@app.post("/payment")
async def make_payment(request: PaymentRequest):
    # Call the logic
    result = dorm_system.payment(request.resident_id, request.paymentdata)
    return {"res": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)