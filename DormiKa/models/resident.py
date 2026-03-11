import datetime
from .payment_gateway import Payment_Method
from .payment import Payment
from .receipt import Receipt
from .cleaning_ticket import *
from .room import *
# import sqlite3


# conn = sqlite3.connect(r"C:\Users\James\Desktop\Ducky-Dicka\main\residents.db")
# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS residents (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     age INTEGER,
#     phone_number TEXT,
#     status TEXT
# )
# """)
# conn.commit()

class Resident:
    ID = 1
    
    def __init__(self, name: str, email: str=None, phone_number: str=None, status: str="ACTIVE"):
        self.__id = f"RS-{Resident.ID:04d}"
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__strike = 0
        self.__date_create = datetime.datetime.now()
        self.__status = status
        self.__payment = None
        self.__member = None
        self.__room_bookings = []
        self.__facility_bookings = []
        self.__contracts = []
        self.__invoices = []
        self.__receipts = []
        self.__booking_share_facility_list = []

        # cursor.execute(
        #     "INSERT INTO residents (name, age, phone_number, status) VALUES ( ?, ?, ?, ?)",
        #     (self.__name, self.__age, self.__phone_number, self.__status)
        # )
        # conn.commit()

        Resident.ID += 1

    @property
    def id(self):
        return self.__id

    @property
    def status(self):
        return self.__status

    @property
    def contracts(self):
        return self.__contracts

    @property
    def invoices(self):
        return self.__invoices

    @property
    def receipts(self):
        return self.__receipts
			
    def set_member(self, member):
        self.__member = member

    def add_contract(self, contract):
        self.__contracts.append(contract)

    def add_invoice(self, invoice):
        self.__invoices.append(invoice)

    def calculate_net_amount(self, amount, discount):
        discount = 1 - discount
        amount = amount * discount
        return amount

    def set_payment(self, payment_method_input, invoice_ids):
        payment_method = Payment_Method.format_payment_method(payment_method_input)
        list_invoice_id = [i.strip().upper() for i in invoice_ids.split(',') if i.strip()]
        if not list_invoice_id:
            raise ValueError("Invoice : format error")
        if len(list_invoice_id) != len(set(list_invoice_id)):
            raise ValueError("Invoice : format error")
        count = 0
        total_amount = 0
        list_selected_invoice = []
        for invoice_id in list_invoice_id:
            for invoice in self.__invoices:
                if invoice_id == invoice.id:
                    count += 1
                    total_amount += invoice.amount
                    list_selected_invoice.append(invoice)
                    break
        if count != len(list_invoice_id):
            raise ValueError("Invoice : format error")
        discount = 0
        if self.__member is not None:
            discount = self.__member.discount
        net_amount = self.calculate_net_amount(total_amount, discount)
        payment = Payment(payment_method, list_selected_invoice, discount, net_amount)
        self.__payment = payment
        return payment
    
    def payment(self, raw_payment):
        if self.__payment == None:
            raise ValueError('Payment : None')
        method = self.__payment.payment_method
        if not method.check_format(raw_payment):
            raise ValueError("Format payment data : invalid")
        for invoice in self.__payment.invoice_list:
            invoice.PAID()
            self.__invoices.remove(invoice)
        receipt = Receipt(self.__payment)
        self.__receipts.append(receipt)
        self.__payment = None
        return receipt
			
    def search_contract_by_id(self, contractId):
        for contract in self.__contracts:
            if contract.id == contractId:
                return contract
        return None
    
    def check_status_cleaning_ticket(self,cleaning_ticket_list):
        for ticket in cleaning_ticket_list:
            if ticket.status == "Requested" or ticket.status == "Cleaning":
                raise ValueError("this room already has cleaning ticket with status Requested or Cleaning")    
        return True
        
    def create_cleaning_ticket(self,resident_id,room_id):
        cleaning_ticket = CleaningTicket(resident_id,room_id)
        return cleaning_ticket
    
    def add_cleaning_ticket(self,room,cleaning_ticket):
        room.cleaning_tickets.append(cleaning_ticket)
        return f"add to room success"