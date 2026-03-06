class Payment:
    ID = 1
    
    def __init__(self, amount, payment_date, payment_gateway):
        self.__id = Payment.ID
        self.__amount = amount
        self.__payment_date = payment_date
        self.__invoices = []
        self.__payment_gateway = payment_gateway

        Payment.ID += 1