from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
import tester as tester_data

from models.dorm import *
from models.enum import *
from models.invoice import *
from models.member import *
from models.maintenance_ticket import *
from models.payment import *
from models.payment_gateway import *
from models.receipt import *
from models.room import *
from models.building import *
from models.room_booking import *
from models.cleaning_ticket import *
from models.facility_booking import *
from models.share_facility import *
from models.staff import *
from models.contract import *
from models.employee import *
from models.resident import *


# ==================== Global Dorm State ====================

dorm: Dorm = None


def init_mock_data():
    global dorm
    dorm = tester_data.init_mock_data()

# ==================== FastMCP ====================


mcp = FastMCP("DormiKa")
init_mock_data()

# ==================================================
# SYSTEM
# ==================================================


@mcp.tool()
def reset() -> dict:
    """
    Reset all mock data back to the initial state.

    Use when:
    - You want to start over with fresh data
    - Something went wrong and you need to restore defaults

    Example prompt:
        "Reset the system to its initial state."
        "Start over with fresh data."
    """
    init_mock_data()
    return {"message": "Mock data has been reset successfully"}


class SystemContractInvoiceRequest(BaseModel):
    employeeId: str = Field(...,
                            description="Employee ID who triggers billing, e.g. EM-0001")


@mcp.tool()
def system_contract_invoice(request: SystemContractInvoiceRequest) -> dict:
    """
    Generate monthly rent invoices for ALL active residents automatically.
    An employee must authorize this batch billing process.

    Use when:
    - It is the start of a new billing month
    - You need to issue rent invoices to all residents at once

    Example prompt:
        "Generate this month's rent invoices for all residents. Employee ID is EM-0001."
        "Run the monthly billing cycle authorized by EM-0002."
    """
    try:
        result = dorm.system_contract_invoice(request.employeeId)
    except Exception as e:
        return {"error": str(e)}
    return {"message": result}


class AddStrikeRequest(BaseModel):
    employeeId: str = Field(...,
                            description="Employee ID who runs the strike check, e.g. EM-0001")


@mcp.tool()
def add_strike(request: AddStrikeRequest) -> dict:
    """
    Check all residents for overdue unpaid invoices and add strikes accordingly.
    Residents with 3+ strikes are moved to the blacklist automatically.

    Strike rules:
    - Invoice unpaid ≥ 1 month  → +1 strike
    - Invoice unpaid ≥ 2 months → +2 strikes
    - Invoice unpaid ≥ 3 months → +3 strikes (blacklisted)

    Use when:
    - Running a monthly overdue payment audit
    - Enforcing payment policy

    Example prompt:
        "Run the overdue invoice check. Employee EM-0001 is authorizing."
        "Add strikes to residents who have unpaid invoices. Use employee EM-0002."
    """
    try:
        result = dorm.add_strike(request.employeeId)
    except Exception as e:
        return {"error": str(e)}
    return {"message": result}

# ==================================================
# RESIDENT
# ==================================================


class SignInRequest(BaseModel):
    name:        str = Field(...,
                             description="Full name (letters only), e.g. Kenny")
    email:       str = Field(...,
                             description="Valid email address, e.g. kenny@example.com")
    phoneNumber: str = Field(...,
                             description="10-digit phone number, e.g. 0812345678")


@mcp.tool()
def sign_in(request: SignInRequest) -> dict:
    """
    Register a new resident account in the dormitory system.
    Validates name (letters only), email format, and phone (10 digits).
    Rejects if the email or phone is blacklisted.

    Use when:
    - A new person wants to register as a resident
    - Someone asks to create a new account

    Example prompt:
        "Register a new resident named Kenny, email kenny@example.com, phone 0812345678."
        "Sign up a new tenant: name Alice, email alice@mail.com, phone 0899999999."
    """
    try:
        result = dorm.sign_in(request.name, request.email, request.phoneNumber)
    except ValueError as e:
        return {"error": str(e)}
    return {"message": result}

# ==================================================
# CONTRACT
# ==================================================


class RequestBookingRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")
    buildingId: str = Field(..., description="Building ID, e.g. A01")
    roomType:   RoomType = Field(
        ..., description="Room type: StudioRoom, StandardRoom, or OneBedRoomRoom")


@mcp.tool()
def request_booking(request: RequestBookingRequest) -> dict:
    """
    !!ignore time closed for testing

    Request to book an available room for a resident.
    Holds the room for 48 hours and creates a DRAFT contract.
    Only works during business hours (08:00–17:00).

    Use when:
    - A resident wants to book a room
    - Starting the contract process

    Example prompt:
        "Resident RS-0001 wants to book a Studio Room in building A01."
        "Book a One Bedroom room in building A01 for resident RS-0002."
    """
    try:
        result = dorm.request_booking(
            request.residentId, request.buildingId, request.roomType)
    except (LookupError, ValueError) as e:
        return {"error": str(e)}
    except PermissionError as e:
        return {"error": f"Permission denied: {str(e)}"}
    return result


class SignContractRequest(BaseModel):
    contractId: str = Field(...,
                            description="Contract ID to sign, e.g. LC-0001")


@mcp.tool()
def sign_contract(request: SignContractRequest) -> dict:
    """
    Sign a DRAFT contract, generating a rent invoice and moving it to PENDING_SIGN status.
    The resident must pay the invoice to fully activate the contract.

    Use when:
    - A resident agrees to the contract terms and wants to proceed
    - After request_booking, the next step is to sign

    Example prompt:
        "Sign contract LC-0001."
        "The resident has agreed — please sign contract LC-0002 and generate the invoice."
    """
    try:
        result = dorm.sign_contract(request.contractId)
    except (LookupError, ValueError) as e:
        return {"error": str(e)}
    return result


class HandoverRequest(BaseModel):
    contractId: str = Field(..., description="Contract ID, e.g. LC-0001")


@mcp.tool()
def complete_handover(request: HandoverRequest) -> dict:
    """
    Complete room handover for a contract.
    Sets the room status to OCCUPIED.

    Use when:
    - The resident is physically moving in and receiving the room

    Example prompt:
        "Complete handover for contract LC-0001."
        "Mark handover complete for contract LC-0002."
    """
    try:
        result = dorm.complete_handover(request.contractId)
    except (LookupError, KeyError, ValueError) as e:
        return {"error": str(e)}
    return result


class PayContractInvoiceRequest(BaseModel):
    invoiceId: str = Field(..., description="Invoice ID to pay, e.g. INV-0001")


@mcp.tool()
def pay_contract_invoice(request: PayContractInvoiceRequest) -> dict:
    """
    Directly pay a contract invoice, activating the contract and marking the room as OCCUPIED.
    This is a one-step payment shortcut for contract invoices only.

    Use when:
    - A resident wants to pay their contract invoice immediately
    - Activating a PENDING_SIGN contract

    Example prompt:
        "Pay contract invoice INV-0001."
        "The resident wants to activate their contract — pay invoice INV-0002."
    """
    try:
        result = dorm.pay_contract_invoice(request.invoiceId)
    except (LookupError, ValueError) as e:
        return {"error": str(e)}
    return result


class ChangeContractRequest(BaseModel):
    residentId:             str = Field(...,
                                        description="Resident ID, e.g. RS-0001")
    currentLeaseContractId: str = Field(
        ..., description="Current lease contract ID, e.g. LC-0001")
    targetRoomId:           str = Field(
        ..., description="Target room ID to move into, e.g. RM-0003")
    moveDate:               str = Field(
        ..., description="Move-in date in YYYY-MM-DD format, e.g. 2026-03-15")


@mcp.tool()
def change_contract(request: ChangeContractRequest) -> dict:
    """
    Move a resident from their current room to a different available room.
    Calculates a prorated upgrade invoice for the remaining days in the month.
    The resident must have no outstanding invoices before changing rooms.

    Use when:
    - A resident wants to upgrade or change their room
    - A room swap is needed

    Example prompt:
        "Resident RS-0001 wants to move from their current room (contract LC-0001) to room RM-0003 on 2026-03-15."
        "Change contract LC-0001 for resident RS-0001 to room RM-0002, moving on 2026-04-01."
    """
    try:
        result = dorm.change_contract(
            request.residentId,
            request.currentLeaseContractId,
            request.targetRoomId,
            request.moveDate,
        )
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================================================
# MAINTENANCE
# ==================================================


class RequestMaintenanceRequest(BaseModel):
    residentId:    str = Field(..., description="Resident ID, e.g. RS-0001")
    roomId:        str = Field(..., description="Room ID, e.g. RM-0001")
    issueCategory: IssueCategory = Field(
        ..., description="Issue type: PLUMBING, ELECTRICAL, or AC")


@mcp.tool()
def request_maintenance(request: RequestMaintenanceRequest) -> dict:
    """
    Submit a maintenance request for a room.
    Automatically assigns an available employee and a matching technician,
    then creates a maintenance ticket.

    Technician matching:
    - PLUMBING   → PlumbingTech
    - ELECTRICAL → ElectricalTech
    - AC         → ACTech

    Use when:
    - A resident reports a broken pipe, electrical issue, or AC problem
    - Any room repair is needed

    Example prompt:
        "Resident RS-0001 reports a plumbing issue in room RM-0001."
        "Room RM-0002 has an electrical problem reported by resident RS-0002."
        "There's an AC issue in room RM-0003, reported by RS-0001."
    """
    try:
        result = dorm.request_maintenance(
            request.residentId, request.roomId, request.issueCategory.value
        )
    except Exception as e:
        return {"error": str(e)}
    return result


class StartMaintenanceRequest(BaseModel):
    technicianId: str = Field(..., description="Technician ID, e.g. TC-0001")
    notes:        Optional[str] = Field(
        None, description="Optional description of the problem, e.g. 'Pipe leaking under the sink'")


@mcp.tool()
def start_maintenance(request: StartMaintenanceRequest) -> dict:
    """
    Technician begins work on their assigned maintenance ticket.
    Sets the ticket status to IN_PROGRESS.

    Use when:
    - A technician is ready to start working on their assigned ticket
    - After request_maintenance, the technician starts the job

    Example prompt:
        "Technician TC-0001 is starting work on their assigned ticket."
        "TC-0002 starts maintenance. Notes: the circuit breaker keeps tripping."
        "Technician TC-0003 begins AC repair. Notes: refrigerant seems low."
    """
    try:
        result = dorm.start_maintenance_workflow(
            request.technicianId, request.notes)
    except Exception as e:
        return {"error": str(e)}
    return result


class FinishMaintenanceRequest(BaseModel):
    technicianId: str = Field(..., description="Technician ID, e.g. TC-0001")


@mcp.tool()
def finish_maintenance(request: FinishMaintenanceRequest) -> dict:
    """
    Mark a maintenance ticket as RESOLVED.
    Calculates the repair cost and generates an invoice for the resident.

    Cost by category:
    - PLUMBING   → 1,000 THB
    - ELECTRICAL →   750 THB
    - AC         →   500 THB

    Use when:
    - A technician has finished the repair
    - Ready to bill the resident for the maintenance

    Example prompt:
        "Technician TC-0001 has finished the repair."
        "Mark TC-0002's job as complete and generate the invoice."
    """
    try:
        result = dorm.finish_maintenance_workflow(request.technicianId)
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================================================
# CLEANING
# ==================================================


class RequestCleaningRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")
    roomId:     str = Field(...,
                            description="Room ID to be cleaned, e.g. RM-0001")


@mcp.tool()
def request_cleaning(request: RequestCleaningRequest) -> dict:
    """
    Submit a room cleaning request for a resident.
    Creates a cleaning ticket. Will fail if the room already has an active
    (Requested or Cleaning) ticket.

    Use when:
    - A resident wants their room cleaned
    - Scheduling a cleaning job

    Example prompt:
        "Resident RS-0001 wants room RM-0001 cleaned."
        "Request a cleaning service for room RM-0002 from resident RS-0002."
    """
    try:
        result = dorm.request_cleaning_room(request.residentId, request.roomId)
    except Exception as e:
        return {"error": str(e)}
    return result


class StartCleaningRequest(BaseModel):
    cleanerId: str = Field(..., description="Cleaner ID, e.g. CL-0001")
    roomId: str = Field(..., description="Room ID to clean, e.g. RM-0001")


@mcp.tool()
def start_cleaning(request: StartCleaningRequest) -> dict:
    """
    Cleaner begins cleaning their assigned room.
    Updates the cleaner's status to WORKING.

    Use when:
    - A cleaner is physically starting to clean the room
    - After request_cleaning, the cleaner starts the job

    Example prompt:
        "Cleaner CL-0001 is starting to clean their assigned room."
        "CL-0002 begins cleaning now."
    """
    try:
        result = dorm.start_cleaning_workflow(
            request.cleanerId, room_id=request.roomId)
    except Exception as e:
        return {"error": str(e)}
    return result


class FinishCleaningRequest(BaseModel):
    cleanerId: str = Field(..., description="Cleaner ID, e.g. CL-0001")
    roomId: str = Field(...,
                        description="Room ID to finish cleaning, e.g. RM-0001")


@mcp.tool()
def finish_cleaning(request: FinishCleaningRequest) -> dict:
    """
    Mark a cleaning job as complete and free the cleaner.
    Generates a cleaning invoice (100 THB) for the resident.

    Use when:
    - A cleaner has finished cleaning the room
    - Ready to bill the resident for the cleaning service

    Example prompt:
        "Cleaner CL-0001 has finished cleaning the room."
        "CL-0002 is done — complete the task and issue the invoice."
    """
    try:
        result = dorm.finish_cleaning_workflow(
            request.cleanerId, request.roomId)
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================================================
# MEMBER
# ==================================================


class CreateMemberRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")
    memberType: str = Field(...,
                            description="Membership tier: STANDARD, PLUS, or PLATINUM")


@mcp.tool()
def create_member(request: CreateMemberRequest) -> dict:
    """
    Assign a membership tier to a resident and create a membership invoice.

    Membership tiers and benefits:
    - STANDARD  →  990 THB / 2% discount on invoices
    - PLUS      → 2,790 THB / 5% discount on invoices
    - PLATINUM  → 9,890 THB / 10% discount on invoices

    Use when:
    - A resident wants to subscribe to a membership plan
    - Assigning discounts to a resident

    Example prompt:
        "Upgrade resident RS-0001 to PLUS membership."
        "Assign PLATINUM membership to resident RS-0002."
        "Resident RS-0003 wants to subscribe to the STANDARD plan."
    """
    try:
        result = dorm.create_member(request.residentId, request.memberType)
    except Exception as e:
        return {"error": str(e)}
    return {"message": result}

# ==================================================
# PAYMENT
# ==================================================


class SelectPaymentRequest(BaseModel):
    residentId:    str = Field(..., description="Resident ID, e.g. RS-0001")
    paymentMethod: str = Field(...,
                               description="Payment method: 'bank_account' or 'card'")
    invoiceIds:    str = Field(
        ..., description="Comma-separated invoice IDs, e.g. 'INV-0001, INV-0002'")


@mcp.tool()
def select_payment(request: SelectPaymentRequest) -> dict:
    """
    Choose a payment method and select which invoices to pay.
    Must be called before the actual pay step.
    If the resident has a membership, a discount is automatically applied.

    Payment methods:
    - 'bank_account' → transfer to dorm bank account, submit reference number
    - 'card'         → fill card number (6 digits), name, expiry (MM/YY), CVV (3 digits)

    Use when:
    - A resident is ready to pay their invoices
    - Step 1 of the 2-step payment process

    Example prompt:
        "Resident RS-0001 wants to pay INV-0001 and INV-0002 via bank transfer."
        "Set up card payment for resident RS-0002 for invoice INV-0003."
    """
    try:
        result = dorm.select_payment_method_and_invoices(
            request.residentId, request.paymentMethod, request.invoiceIds
        )
    except Exception as e:
        return {"error": str(e)}
    return result


class PayRequest(BaseModel):
    residentId:  str = Field(..., description="Resident ID, e.g. RS-0001")
    paymentData: str = Field(
        ...,
        description=(
            "Payment data based on the selected method:\n"
            "- bank_account: Reference number (11–20 alphanumeric chars), e.g. 'REF-ABC1234567'\n"
            "- card: 'CARD_NUMBER, NAME, MM/YY, CVV' e.g. '123456, Kenny, 12/27, 123'"
        )
    )


@mcp.tool()
def pay(request: PayRequest) -> dict:
    """
    Submit payment data to confirm and settle the selected invoices.
    Must call select_payment first to choose method and invoices.
    On success, generates a receipt and marks invoices as PAID.

    Use when:
    - Completing the payment after select_payment
    - Step 2 of the 2-step payment process

    Example prompt (bank):
        "Resident RS-0001 submits bank transfer reference REF-XYZ9876543."
    Example prompt (card):
        "Resident RS-0001 pays by card: number 123456, name Kenny, expiry 12/27, CVV 123."
    """
    try:
        result = dorm.payment_system(request.residentId, request.paymentData)
    except Exception as e:
        return {"error": str(e)}
    return {"message": result}

# ==================================================
# INVOICE
# ==================================================


class DisplayInvoiceRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")


@mcp.tool()
def display_invoice(request: DisplayInvoiceRequest) -> dict:
    """
    List all pending (unpaid) invoices for a resident.

    Use when:
    - A resident asks what they owe
    - Checking outstanding balances before payment

    Example prompt:
        "Show all invoices for resident RS-0001."
        "What does RS-0002 owe?"
        "List unpaid bills for RS-0003."
    """
    try:
        result = dorm.display_invoice(request.residentId)
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================================================
# RECEIPT
# ==================================================


class DisplayReceiptRequest(BaseModel):
    residentId: str = Field(..., description="Resident ID, e.g. RS-0001")


@mcp.tool()
def display_receipt(request: DisplayReceiptRequest) -> dict:
    """
    List all payment receipts for a resident.

    Use when:
    - A resident wants proof of past payments
    - Checking payment history

    Example prompt:
        "Show all receipts for resident RS-0001."
        "What payments has RS-0002 made?"
        "Get payment history for resident RS-0003."
    """
    try:
        result = dorm.display_receipt(request.residentId)
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================================================
# FACILITY
# ==================================================


class BookFacilityRequest(BaseModel):
    residentId:  str = Field(..., description="Resident ID, e.g. RS-0001")
    buildingId:  str = Field(...,
                             description="Building ID where facility is located, e.g. A01")
    facilityId:  str = Field(..., description="Facility ID, e.g. SHARE-0001")
    bookingTime: str = Field(
        ..., description="Booking time in 'YYYY-MM-DD HH:MM:SS' format, e.g. '2026-03-15 14:00:00'")


@mcp.tool()
def book_share_facility(request: BookFacilityRequest) -> dict:
    """
    Book a shared facility (meeting room or washing machine) in a building.
    Will fail if the facility is already booked at the requested time.
    Automatically creates a facility usage invoice for the resident.

    Facility costs:
    - Meeting Room     → 100 THB
    - Washing Machine  →  50 THB

    Use when:
    - A resident wants to reserve a shared facility
    - Booking a washing machine or meeting room slot

    Example prompt:
        "Resident RS-0001 wants to book facility SHARE-0001 in building A01 at 2026-03-15 14:00:00."
        "Book the washing machine (SHARE-0002) for RS-0002 in building A01 at 2026-04-01 09:00:00."
        "Reserve meeting room SHARE-0003 in building A01 for resident RS-0001 at 2026-03-20 10:00:00."
    """
    try:
        result = dorm.booking_share_facility(
            request.residentId,
            request.facilityId,
            request.buildingId,
            request.bookingTime,
        )
    except Exception as e:
        return {"error": str(e)}
    return result

# ==================== Entrypoint ====================


if __name__ == "__main__":
    mcp.run()
