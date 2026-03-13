from datetime import datetime
from .payment_gateway import Payment_Method
from .payment import Payment
from .receipt import Receipt
from .cleaning_ticket import *
from .room import *
from .enum import AccountStatus, CleaningStatus, InvoiceStatus


class Resident:
    ID = 1

    def __init__(self, name: str, email: str = None, phone_number: str = None,
                 status: AccountStatus = AccountStatus.ACTIVE):
        self.__id = f"RS-{Resident.ID:04d}"
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__status = status
        self.__strike = 0
        self.__date_create = datetime.now()
        self.__payment = None
        self.__member = None
        self.__room_bookings = []
        self.__contracts = []
        self.__invoices = []
        self.__receipts = []
        self.__booking_share_facility_list = []

        Resident.ID += 1

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def id(self):
        return self.__id

    @property
    def strike(self):
        return self.__strike

    def add_strike(self, amount: int):
        self.__strike += amount

    def reset_strike(self):
        self.__strike = 0

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: AccountStatus):
        self.__status = new_status

    @property
    def contracts(self):
        return self.__contracts

    @property
    def invoices(self):
        return self.__invoices

    @property
    def receipts(self):
        return self.__receipts

    @property
    def booking_share_facility_list(self):
        return self.__booking_share_facility_list

    def set_member(self, member):
        self.__member = member

    def add_contract(self, contract):
        self.__contracts.append(contract)

    def add_invoice(self, invoice):
        self.__invoices.append(invoice)

    def add_booking_share_facility(self, booking):
        self.__booking_share_facility_list.append(booking)

    def calculate_net_amount(self, amount, discount):
        discount = 1 - discount
        amount = amount * discount
        return amount

    def set_payment(self, payment_method_input, invoice_ids):
        payment_method = Payment_Method.format_payment_method(
            payment_method_input)
        list_invoice_id = [i.strip().upper()
                           for i in invoice_ids.split(',') if i.strip()]
        if not list_invoice_id:
            raise ValueError("Invoice : format error")
        if len(list_invoice_id) != len(set(list_invoice_id)):
            raise ValueError("Invoice : format error")

        # Keep previously selected invoices so repeated calls can build a basket.
        list_selected_invoice = []
        existing_ids = set()
        if self.__payment is not None:
            if type(self.__payment.payment_method) != type(payment_method):
                raise ValueError(
                    "Payment method already selected; complete payment first")
            list_selected_invoice.extend(self.__payment.invoice_list)
            existing_ids = {
                invoice.id for invoice in self.__payment.invoice_list}

        count = 0
        for invoice_id in list_invoice_id:
            if invoice_id in existing_ids:
                count += 1
                continue
            for invoice in self.__invoices:
                if invoice_id == invoice.id and invoice.status == InvoiceStatus.UNPAID:
                    count += 1
                    list_selected_invoice.append(invoice)
                    existing_ids.add(invoice.id)
                    break
        if count != len(list_invoice_id):
            raise ValueError("Invoice : invalid id or already paid")

        total_amount = sum(invoice.amount for invoice in list_selected_invoice)
        discount = 0
        if self.__member is not None:
            discount = self.__member.discount
        net_amount = self.calculate_net_amount(total_amount, discount)
        payment = Payment(
            payment_method, list_selected_invoice, discount, net_amount)
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

    def check_status_cleaning_ticket(self, cleaning_ticket_list):
        # FIX: Was comparing ticket.status (a CleaningStatus enum) against raw strings.
        #      Now compares against CleaningStatus enum values.
        for ticket in cleaning_ticket_list:
            if ticket.status == CleaningStatus.REQUESTED or ticket.status == CleaningStatus.CLEANING:
                raise ValueError(
                    "this room already has cleaning ticket with status Requested or Cleaning")
        return True

    def create_cleaning_ticket(self, resident_id, room_id):
        cleaning_ticket = CleaningTicket(resident_id, room_id)
        return cleaning_ticket

    def add_cleaning_ticket(self, room, cleaning_ticket):
        room.cleaning_tickets.append(cleaning_ticket)
        return f"add to room success"

    def add_facility_booking(self, facility_booking):
        """Add a facility booking to the resident's booking list"""
        self.__booking_share_facility_list.append(facility_booking)
        return facility_booking

    def add_booking_share_facility(self, booking):
        """Add a booking to the resident's booking list"""
        self.__booking_share_facility_list.append(booking)
        return booking

    def get_facility_bookings(self):
        """Get all facility bookings for this resident"""
        return self.__booking_share_facility_list
