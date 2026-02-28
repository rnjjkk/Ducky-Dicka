class Member:
    def __init__(self, discount_amount):
        self.__discount_amount = discount_amount
        self.__type = None

class Share_Facility_Member(Member):
    def check_status(self):
        pass

    def calculate_discount(self):
        pass

class Service_Member(Member):
    def check_paydate(self):
        pass

    def calculate_discount(self):
        pass

class Contract_Member(Member):
    def check_contract_range(self):
        pass

    def calculate_discount(self):
        pass