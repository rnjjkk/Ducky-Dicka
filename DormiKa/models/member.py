from abc import ABC
from .enum import MemberType


class Member(ABC):
    def __init__(self, member_type: MemberType, discount: float):
        self.__member_type = member_type
        self.__discount = discount

    @property
    def member_type(self):
        return self.__member_type

    @property
    def discount(self):
        return self.__discount


class Standard_Member(Member):
    def __init__(self):
        super().__init__(member_type=MemberType.STANDARD, discount=0.02)


class Plus_Member(Member):
    def __init__(self):
        super().__init__(member_type=MemberType.PLUS, discount=0.05)


class Platinum_Member(Member):
    def __init__(self):
        super().__init__(member_type=MemberType.PLATINUM, discount=0.10)
