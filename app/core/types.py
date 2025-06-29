from enum import Enum, unique


@unique
class UserType(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


@unique
class TokenType(str, Enum):
    REFRESH = "REFRESH"
    ACCESS = "ACCESS"


@unique
class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"


@unique
class Gender(str, Enum):
    ANY = "ANY"
    MALE = "MALE"
    FEMALE = "FEMALE"


@unique
class PhysicalActivity(str, Enum):
    HIGH = "HIGH"
    AVERAGE = "AVERAGE"
    LOW = "LOW"
    DISABLED = "DISABLED"


@unique
class SportActivity(str, Enum):
    Phitness = "HIGH"
    AVERAGE = "AVERAGE"
    LOW = "LOW"
    DISABLED = "DISABLED"
