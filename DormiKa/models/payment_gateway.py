import re
from abc import ABC, abstractmethod

# ================== Payment_Method
class Payment_Method(ABC):
    @staticmethod
    def format_payment_method(payment_method_input):
        m = payment_method_input.strip().lower()
        for cls in Payment_Method.__subclasses__():
            if cls.type == m:
                return cls()
        raise ValueError("Payment_Method : format error")

    @abstractmethod
    def payment_format(self):
        pass

    @abstractmethod
    def check_format(self, raw_payment):
        pass

class Bank_Account(Payment_Method):
    type = 'bank_account'
    dorm_bank_account_number = '000-0-00000-0'
    bank = 'A-bank'

    def payment_format(self):
        return f'{self.bank} : {self.dorm_bank_account_number}\nBring back the Receipt Reference No. to confirm your payment'

    def check_format(self, raw_payment):
        if not isinstance(raw_payment, str):
            raise ValueError("Format payment data : invalid")
        ref_no = raw_payment.strip()
        if ref_no == "":
            raise ValueError("Format payment data : invalid")
        if not (10 < len(ref_no) <= 20):
            raise ValueError("Format payment data : invalid")
        if not re.fullmatch(r"[A-Za-z0-9-]+", ref_no):
            raise ValueError("Format payment data : invalid")
        return True

class Card(Payment_Method):
    type = 'card'
    format = "Fill out the form below to confirm your payment\n[Card Number: 6 digit], [Cardholder Name: Nickname], [Expiry Date: MM/YY], [CVV/CVC: 3 digit] "

    def payment_format(self):
        return self.format

    def check_format(self, raw_payment):
        if not isinstance(raw_payment, str):
            raise ValueError("Format payment data : invalid")
        parts = [p.strip() for p in raw_payment.split(',')]
        if len(parts) != 4:
            raise ValueError("Format payment data : invalid")
        card_no, name, expiry, cvv = parts
        if not (card_no.isdigit() and len(card_no) == 6):
            raise ValueError("Format payment data : invalid")
        if not name:
            raise ValueError("Format payment data : invalid")
        if not re.fullmatch(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry):
            raise ValueError("Format payment data : invalid")
        if not (cvv.isdigit() and len(cvv) == 3):
            raise ValueError("Format payment data : invalid")
        return True
