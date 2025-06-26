from enum import Enum, unique


@unique
class UserType(str, Enum):
    USER = "USER"


@unique
class TokenType(str, Enum):
    REFRESH = "REFRESH"
    ACCESS = "ACCESS"


@unique
class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
