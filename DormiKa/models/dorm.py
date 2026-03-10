class Dorm:
    def __init__(self, name: str):
        self.__name: str = name
        self.__buildings: list = []
        self.__residents: list = []
        self.__employees: list = []
        self.__technicians: list = []
        self.__cleaner: list = []

    def show_success(self, success):
        print(success)
        return success

    def show_error(self, error):
        print(error)
        return error

    def add_employee(self, employee):
        self.__employees.append(employee)

    def add_resident(self, resident):
        self.__residents.append(resident)

    def add_operation_staff(self, employee):
        self.__employees.append(employee)

    def add_technician(self, technician):
        self.__technicians.append(technician)

    def add_building(self, building):
        self.__buildings.append(building)

    def search_employee_by_id(self, employee_id):
        for employee in self.__employees :
            if employee.id == employee_id:
                return employee
        raise PermissionError("Employee id : not found")
    
    def search_resident_by_id(self, resident_id):
        for resident in self.__residents :
            if resident.id == resident_id:
                return resident
        raise PermissionError("Resident id : not found")

    def search_room_by_id(self, room_id):
        for building in self.__buildings:
            for room in building.rooms:
                if room.id == room_id:
                    return room
        raise PermissionError("Room id : not found")

    def search_available_employee(self):
        for employee in self.__employees:
            if employee.status == "AVAILABLE":
                return employee
        raise ValueError("No employee are available at the moment")

    # def search_capability_technician(self, capability):
    #     for technician in self.__technicians:
    #         for skill in technician.skills:
    #             if skill == capability and technician.status == "AVAILABLE":
    #                 return technician
    #     return None

    def request_maintenance(self, resident_id, room_id, issue_category):
        resident = self.search_resident_by_id(resident_id)
        if resident is None:
            return {"error": "resident not found!"}

        room = self.search_room_by_id(room_id)
        if room is None:
            return {"error": "room not found!"}

        employee = self.search_available_employee()
        if employee is None:
            return {"error": "no available staff!"}
        
        return employee.start_maintenance(
            resident, 
            self.__technicians,
            room,
            issue_category
        )
    
    # ไม่ใช้ try-except ใน model layer — ให้ exception propagate ขึ้นไปจัดการที่ API layer แทน

    def system_contract_invoice(self, employee_ID_input):
        employee = self.search_employee_by_id(employee_ID_input)
        for resident in self.__residents:
            for contract in resident.contract_list:
                monthly_rent = contract.room.monthly_rent
                room_id = contract.room.id
                invoice = employee.create_contract_invoice(monthly_rent, room_id)
                resident.add_invoice(invoice)
        s = 'system_contract_invoice : success'
        self.show_success(s)

    def select_payment_method_and_invoices(self, Resident_ID_input, payment_method_input, invoice_ids):
        resident = self.search_resident_by_id(Resident_ID_input)
        payment = resident.set_payment(payment_method_input, invoice_ids)
        format = payment.payment_method.payment_format()
        net_amount = payment.net_amount
        s = f'select_payment_method_and_invoices : success\nAmount to be paid : {net_amount}\n{format}'
        self.show_success(s)

    def payment_system(self, Resident_ID_input, paymentdata):
        resident = self.search_resident_by_id(Resident_ID_input)
        receipt = resident.payment(paymentdata)
        receipt_id = receipt.ID
        s = f'payment_system : success\nreceipt : {receipt_id}'
        self.show_success(s)