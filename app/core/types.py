from enum import Enum, unique


@unique
class UserType(str, Enum):
    user = "user"


@unique
class TokenType(str, Enum):
    REFRESH = "REFRESH"
    ACCESS = "ACCESS"
