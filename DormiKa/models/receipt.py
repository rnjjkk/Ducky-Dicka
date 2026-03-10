from datetime import datetime

# ================== Receipt
class Receipt:
    __running_number = 1

    def __init__(self, payment):
        self.__id = f"RC-{Receipt.__running_number:04d}"
        Receipt.__running_number += 1
        self.__payment = payment
        self.__date_create = datetime.now()

    @property
    def ID(self):
        return self.__id