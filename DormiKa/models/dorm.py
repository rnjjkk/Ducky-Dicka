from encodings.punycode import digits

from .enum import *
from .contract import *
from .room import *
from .resident import *
from .facility_booking import *
from .invoice import Invoice
import re
import datetime
from pprint import pprint


class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technicians: list = []
        self.__cleaners: list = []
        self.__blacklist: list = []

    @property
    def name(self):
        return self.__name

    @property
    def buildings(self):
        return self.__buildings

    @property
    def residents(self):
        return self.__residents

    @property
    def employees(self):
        return self.__employees

    @property
    def technicians(self):
        return self.__technicians

    @property
    def cleaners(self):
        return self.__cleaners

    def show_success(self, success):
        pprint(success)
        return success

    def show_error(self, error):
        pprint(error)
        return error

    def add_employee(self, employee):
        self.__employees.append(employee)

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, employee):
        self.__employees.append(employee)

    def add_technician(self, technician):
        self.__technicians.append(technician)

    def add_cleaner(self, cleaner):
        self.__cleaners.append(cleaner)

    def add_building(self, building):
        self.__buildings.append(building)

    def search_employee_by_id(self, employee_id):
        for employee in self.__employees:
            if employee.id == employee_id:
                return employee
        raise PermissionError("Employee id : not found")

    def search_resident_by_id(self, resident_id):
        for resident in self.__residents:
            if resident.id == resident_id:
                return resident
        raise PermissionError("Resident id : not found")

    def search_room_by_id(self, room_id):
        for building in self.__buildings:
            for room in building.rooms:
                if room.id == room_id:
                    return room
        raise PermissionError("Room id : not found")

    def search_room_by_contracts(self, resident, room_id):
        for contract in resident.contracts:
            if contract.room.id == room_id:
                return contract.room
        raise ValueError("request wrong room resident doesn't in contract")

    def search_building_by_id(self, building_id):
        for building in self.__buildings:
            if building.id == building_id:
                return building
        raise PermissionError("Building id : not found")

    def search_technician_by_id(self, technician_id):
        for technician in self.__technicians:
            if technician.id == technician_id:
                return technician
        raise ValueError(f"Technician '{technician_id}' not found")

    def search_cleaner_by_id(self, cleaner_id):
        for cleaner in self.__cleaners:
            if cleaner.id == cleaner_id:
                return cleaner
        raise ValueError(f"Cleaner '{cleaner_id}' not found")

    def start_cleaning_workflow(self, cleaner_id, room_id):
        try:
            from .enum import CleaningStatus
            cleaner = self.search_cleaner_by_id(cleaner_id)
            room = self.search_room_by_id(room_id)

            if room not in cleaner.assigned_rooms:
                cleaner.assigned_rooms.append(room)

            ticket = None
            for t in room.cleaning_tickets:
                if t.room_id == room_id and t.status != CleaningStatus.FINISHED:
                    ticket = t
                    break

            if ticket is None:
                raise ValueError(
                    f"No active cleaning ticket found for room {room_id}")

            ticket.status = CleaningStatus.CLEANING
            cleaner.status = "WORKING"

            return {
                "cleaner_id": cleaner.id,
                "ticket_id": ticket.id,
                "room_id": ticket.room_id,
                "status": ticket.status.value,
            }
        except ValueError as e:
            return self.show_error({"error": str(e)})

    def finish_cleaning_workflow(self, cleaner_id, room_id):
        try:
            from .enum import CleaningStatus
            cleaner = self.search_cleaner_by_id(cleaner_id)
            room = self.search_room_by_id(room_id)

            ticket = None
            for t in room.cleaning_tickets:
                if t.room_id == room_id and t.status != CleaningStatus.FINISHED:
                    ticket = t
                    break

            if ticket is None:
                raise ValueError(
                    f"No active cleaning ticket found for room {room_id}")

            ticket.status = CleaningStatus.FINISHED
            if room in cleaner.assigned_rooms:
                cleaner.assigned_rooms.remove(room)
            cleaner.status = "AVAILABLE"

            resident = self.search_resident_by_room_id(room_id)
            if resident:
                cleaning_invoice = Invoice(
                    InvoiceType.CLEANER,
                    ticket.id,
                    ticket.cost,
                    InvoiceStatus.UNPAID
                )
                resident.add_invoice(cleaning_invoice)

            return {
                "cleaner_id": cleaner.id,
                "cleaner_status": cleaner.status,
                "ticket_id": ticket.id,
                "room_id": ticket.room_id,
                "status": ticket.status.value,
                "invoice_id": cleaning_invoice.id if resident else None,
                "cost": ticket.cost if resident else None,
            }
        except ValueError as e:
            return self.show_error({"error": str(e)})

    def search_contract_by_id(self, contract_id):
        for resident in self.__residents:
            for contract in resident.contracts:
                if contract.id == contract_id:
                    return resident, contract
        raise ValueError(f"Contract '{contract_id}' not found")

    def search_invoice_by_id(self, invoice_id):
        for resident in self.__residents:
            for invoice in resident.invoices:
                if invoice.id == invoice_id:
                    return resident, invoice
        raise ValueError(f"Invoice '{invoice_id}' not found")

    def request_booking(self, resident_id, building_id, room_type):
        # 1. find resident
        resident = self.search_resident_by_id(resident_id)

        # 2. check account status
        if resident.status == AccountStatus.SUSPEND:
            raise PermissionError("Account is suspended")
        if resident.status == AccountStatus.CLOSED:
            raise PermissionError("Account is closed")

        # 3. check business hours
        # if not (8 <= datetime.datetime.now().hour <= 17):
        #     raise ValueError("Outside business hours (08:00–17:00)")

        # 3. find building and hold an available room
        building = self.search_building_by_id(building_id)
        room = building.find_and_hold_available_room_by_type(room_type)

        # 4. create contract (DRAFT)
        contract = Contract(resident, room, status=ContractStatus.DRAFT)
        resident.add_contract(contract)

        return {
            "contract_id": contract.id,
            "resident_id": resident.id,
            "room_id": room.id,
            "room_status": room.status.value,
            "room_type": room.type.value,
            "contract_status": contract.status.value,
        }

    def sign_contract(self, contract_id):
        # 1. find contract
        resident, contract = self.search_contract_by_id(contract_id)

        # 2. validate — must be DRAFT
        contract.validate_for_signing()

        # 3. create contract invoice from room price
        invoice = Invoice(
            InvoiceType.CONTRACT,
            contract.room.id,
            contract.room.monthly_rent, InvoiceStatus.UNPAID
        )
        resident.add_invoice(invoice)

        # 4. link invoice to contract and advance status
        contract.invoice_id = invoice.id
        contract.status = ContractStatus.PENDING_SIGN

        return {
            "invoice_id": invoice.id,
            "contract_id": contract.id,
            "amount": invoice.amount,
            "contract_status": contract.status.value,
        }

    def pay_contract_invoice(self, invoice_id):
        # 1. find invoice
        resident, invoice = self.search_invoice_by_id(invoice_id)

        # 2. validate not already paid
        invoice.validate_for_payment()

        # 3. find the contract linked to this invoice
        contract = next(
            (c for c in resident.contracts if c.invoice_id == invoice_id), None
        )
        if contract is None:
            raise ValueError(f"No contract linked to invoice '{invoice_id}'")

        # 4. mark paid and activate contract + room
        invoice.status = InvoiceStatus.PAID
        contract.status = ContractStatus.ACTIVE
        contract.room.status = RoomStatus.OCCUPIED

        return {
            "invoice_id": invoice.id,
            "contract_id": contract.id,
            "contract_status": contract.status.value,
            "room_id": contract.room.id,
            "room_status": contract.room.status.value,
        }

    def complete_handover(self, contract_id: str):
        # 1. find resident and contract
        resident, contract = self.search_contract_by_id(contract_id)

        # 2. validate contract status (must be ACTIVE or PENDING_SIGN)
        contract.validate_contract_status_for_handover()

        # 3. mark room as OCCUPIED
        room = contract.room
        room.status = RoomStatus.OCCUPIED

        return {
            "contract_id": contract.id,
            "resident_id": resident.id,
            "room_id": room.id,
            "room_status": room.status.value,
            "contract_status": contract.status.value,
        }

    def search_resident_by_room_id(self, room_id):
        for resident in self.__residents:
            for contract in resident.contracts:
                if contract.room.id == room_id and contract.status == ContractStatus.ACTIVE:
                    return resident
        raise ValueError(f"No active resident found for room '{room_id}'")

    def search_available_employee(self):
        for employee in self.__employees:
            if employee.status == AvailabilityStatus.AVAILABLE:
                return employee
        raise ValueError("No employee are available at the moment")

    def request_cleaning_room(self, resident_id, room_id):
        # 1.search resident by id
        resident = self.search_resident_by_id(resident_id)

        # 2. serach room by id (room resident input)
        room_input = self.search_room_by_id(room_id)

        # 3. search room by contracts (room in resident contract)
        room_in_contract = self.search_room_by_contracts(
            resident, room_input.id)

        # 4. get cleaning ticket list
        cleaning_ticket_list = room_in_contract.cleaning_tickets

        # 5. check status cleaning ticket
        try:
            if resident.check_status_cleaning_ticket(cleaning_ticket_list):
                # 6. create cleaning ticket
                cleaning_ticket = resident.create_cleaning_ticket(
                    resident_id, room_id)
                # 7. add cleaning ticket to room
                resident.add_cleaning_ticket(room_in_contract, cleaning_ticket)
                # 8. request success
                s = {
                    "reporter": resident.id,
                    "room_id": cleaning_ticket.room_id,
                    "ticket id": cleaning_ticket.id,
                    "report_time": str(cleaning_ticket.report_time),
                    "cost": cleaning_ticket.cost,
                    "status": cleaning_ticket.status.value
                }
                return self.show_success(s)
            else:
                return self.show_error({"error": "Cleaning ticket already exists or invalid status"})

        except Exception as e:
            return self.show_error({"error": str(e)})

    def booking_share_facility(self, resident_id, facility_id, building_id, booking_time):
        try:
            # 1. search resident by id
            resident = self.search_resident_by_id(resident_id)

            # 2. search building by id
            building = self.search_building_by_id(building_id)

            # 3. search share facility in building
            share_facility = building.get_share_facility_by_id(facility_id)

            # 4. check all residents' booking list for time overlap
            for r in self.__residents:
                for booking in r.booking_share_facility_list:
                    if booking.check_booking_time(facility_id, booking_time):
                        return self.show_error({"error": "this share facility already booking"})

            # 5. create booking
            booking = share_facility.create_booking(
                resident_id, facility_id, building_id, booking_time)

            # 6. add booking to resident
            resident.add_booking_share_facility(booking)

            # 7. create invoice (fix cost)
            invoice = share_facility.create_share_facility_invoice(
                resident_id, booking)

            # 8. add invoice to resident
            resident.add_invoice(invoice)

            return self.show_success({
                "booking_id": booking.id,
                "share_facility_id": facility_id,
                "building_id": building_id,
                "booking_time": booking_time,
                "invoice_id": invoice.id,
                "cost": invoice.amount
            })

        except (PermissionError, ValueError) as e:
            return self.show_error({"error": str(e)})
        except Exception as e:
            return self.show_error({"error": str(e)})

    def request_maintenance(self, resident_id, room_id, issue_category):
        resident = self.search_resident_by_id(resident_id)

        room = self.search_room_by_id(room_id)

        employee = self.search_available_employee()

        return employee.start_maintenance(
            resident,
            self.__technicians,
            room,
            issue_category.upper()
        )

    def start_maintenance_workflow(self, technician_id, notes=None):
        technician = self.search_technician_by_id(technician_id)
        return technician.start_maintenance(notes)

    def finish_maintenance_workflow(self, technician_id):
        # Find and complete maintenance for technician
        technician = self.search_technician_by_id(technician_id)
        ticket = technician.complete_task()

        # Create invoice for maintenance work
        invoice = Invoice(
            InvoiceType.MAINTENANCE,
            ticket.room_id, ticket.cost, InvoiceStatus.UNPAID
        )
        resident = self.search_resident_by_room_id(ticket.room_id)
        resident.add_invoice(invoice)

        return {
            "staff_id": technician.id,
            "ticket_id": ticket.id,
            "room_id": ticket.room_id,
            "issue_category": ticket.issue_category,
            "ticket_status": ticket.status.value,
            "start_time": str(ticket.start_time),
            "end_time": str(ticket.end_time),
            "cost": ticket.cost,
            "invoice": {
                "id": invoice.id,
                "type": InvoiceType.MAINTENANCE.value,
                "amount": invoice.amount,
                "status": InvoiceStatus.UNPAID.value,
            },
            "resident_id": resident.id,
        }

    def system_contract_invoice(self, employeeId):
        employee = self.search_employee_by_id(employeeId)
        residents = []
        for resident in self.__residents:
            for contract in resident.contracts:
                monthly_rent = contract.room.monthly_rent
                room_id = contract.room.id
                invoice = employee.create_contract_invoice(
                    monthly_rent,
                    room_id,
                )
                resident.add_invoice(invoice)
                residents.append(resident)
        res = {"system_contract_invoice": "success"}
        self.show_success(res)
        return {
            "system_contract_invoice": "success",
            "employee_id": employeeId,
            "residents": [
                {
                    "id": resident.id,
                    "invoice": [invoice.id for invoice in resident.invoices]
                } for resident in residents
            ]
        }

    def select_payment_method_and_invoices(self, Resident_ID_input, payment_method_input, invoice_ids):
        resident = self.search_resident_by_id(Resident_ID_input)
        payment = resident.set_payment(payment_method_input, invoice_ids)
        payment_format = payment.payment_method.payment_format()
        selected_invoices = [
            {
                "invoice_id": invoice.id,
                "amount": invoice.amount,
                "status": invoice.status.value,
            }
            for invoice in payment.invoice_list
        ]
        gross_amount = sum(invoice["amount"] for invoice in selected_invoices)
        net_amount = payment.net_amount

        result = {
            "select_payment_method_and_invoices": "success",
            "resident_id": resident.id,
            "payment_method": payment_method_input,
            "selected_invoices": selected_invoices,
            "summary": {
                "gross_amount": gross_amount,
                "net_amount": net_amount,
                "discount_amount": gross_amount - net_amount,
            },
            "payment_format": payment_format,
        }
        return self.show_success(result)

    def payment_system(self, Resident_ID_input, paymentdata):
        resident = self.search_resident_by_id(Resident_ID_input)
        receipt = resident.payment(paymentdata)
        receipt_id = receipt.id
        s = f'payment_system : success\nreceipt : {receipt_id}'
        self.show_success(s)
        return s

    def change_contract(self,
                        residentId,
                        currentLeaseContractId,
                        targetRoomId,
                        moveDate
                        ):
        resident = self.search_resident_by_id(residentId)
        if resident is None:
            return {"response": "resident not found"}

        current_contract = resident.search_contract_by_id(
            currentLeaseContractId)
        if current_contract is None:
            return {"response": "current contract not found"}

        if current_contract.status == ContractStatus.EXPIRED:
            return {"response": "expired contract not found"}

        target_room = self.search_room_by_id(targetRoomId)

        if target_room.status != RoomStatus.AVAILABLE:
            print(target_room.status, RoomStatus.AVAILABLE)
            return {"response": "target room not available"}

        unpaid_invoices = [
            invoice for invoice in resident.invoices
            if invoice.status == InvoiceStatus.UNPAID
        ]
        if len(unpaid_invoices) > 0:
            return {"response": "please settle existing invoices before changing contract"}

        invoice = current_contract.calculate_upgrade_amount(
            target_room.monthly_rent, moveDate)
        old_room = current_contract.room
        old_room.status = RoomStatus.AVAILABLE
        current_contract.room = target_room
        target_room.status = RoomStatus.OCCUPIED

        resident.add_invoice(invoice)
        return {
            "resident": {
                "id": resident.id,
                "new_room": target_room.id,
                "invoice": {
                    "id": invoice.id,
                    "amount": invoice.amount,
                } if invoice else None,
            },
            "old-room": {
                "id": old_room.id,
                "status": old_room.status.value,
            }
        }

    def display_invoice(self, resident_id_input):
        resident = self.search_resident_by_id(resident_id_input)
        invoices = [
            {
                "invoice_id": invoice.id,
                "amount": invoice.amount,
                "status": invoice.status.value,
            }
            for invoice in resident.invoices
            if invoice.status == InvoiceStatus.UNPAID
        ]

        result = {
            "resident_id": resident.id,
            "invoices": invoices,
        }
        return self.show_success(result)

    def display_receipt(self, resident_id_input):
        resident = self.search_resident_by_id(resident_id_input)
        receipts = [
            {
                "receipt_id": receipt.id,
            }
            for receipt in resident.receipts
        ]

        result = {
            "resident_id": resident.id,
            "strike": resident.strike,
            "receipt_count": len(receipts),
            "receipts": receipts,
        }
        return self.show_success(result)

    def create_member(self, resident_id_input, type_member):
        resident = self.search_resident_by_id(resident_id_input)
        employee = self.search_available_employee()
        invoice = employee.assign_member(resident, type_member)
        resident.add_invoice(invoice)
        s = f"create_member: success, ID: {invoice.id}, amount: {invoice.amount}"
        self.show_success(s)
        return {
            "response": "success",
            "invoice_id": invoice.id,
            "amount": invoice.amount,
        }

    def add_strike(self, employee_ID_input):
        employee = self.search_employee_by_id(employee_ID_input)
        now = datetime.datetime.now()
        residents_to_blacklist = []

        for resident in self.__residents:
            max_strike = 0

            for invoice in resident.invoices:
                if invoice.status == InvoiceStatus.PAID:
                    continue

                age = now - invoice.date_create
                months_old = age.days // 30

                if months_old >= 3:
                    strike = 3
                elif months_old >= 2:
                    strike = 2
                elif months_old >= 1:
                    strike = 1
                else:
                    strike = 0

                if strike > max_strike:
                    max_strike = strike

            if max_strike > 0:
                resident.add_strike(max_strike)

            if resident.strike >= 3:
                residents_to_blacklist.append(resident)

        for resident in residents_to_blacklist:
            self.__residents.remove(resident)
            self.__blacklist.append(resident)

        s = 'add_strike : success'
        self.show_success(s)
        return s

    def sign_in(self, name, email, phone_number):
        # validate name
        if not name.replace(" ", "").isalpha():
            e = {"sign_in": "error, name must be letters only"}
            self.show_error(e)
            raise ValueError(e)

        # validate email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            e = {"sign_in": "error, invalid email format"}
            self.show_error(e)
            raise ValueError(e)

        # validate phone
        if not phone_number.replace("-", "").isdigit() or len(phone_number.replace("-", "").strip()) != 10:
            e = {"sign_in": "error, phone number must be 10 digits"}
            self.show_error(e)
            raise ValueError(e)

        # check blacklist
        for blacklisted in self.__blacklist:
            if blacklisted.email == email or blacklisted.phone_number == phone_number:
                e = {"sign_in": "error, email or phone number is blacklisted"}
                self.show_error(e)
                raise ValueError(e)

        resident = Resident(name, email, phone_number)
        self.add_resident(resident)
        s = {
            "sign_in": "success",
            "your_id_is": resident.id
        }
        return self.show_success(s)
