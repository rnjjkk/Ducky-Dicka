# ================== Payment
class Payment:
    def __init__(self, payment_method, list_selected_invoice, discount, net_amount):
        self.__payment_method = payment_method
        self.__invoice_list = list_selected_invoice
        self.__discount = discount
        self.__net_amount = net_amount

    @property
    def payment_method(self):
        return self.__payment_method

    @property
    def invoice_list(self):
        return self.__invoice_list

    @property
    def net_amount(self):
        return self.__net_amount