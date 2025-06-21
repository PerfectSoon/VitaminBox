from enum import Enum, unique


@unique
class UserType(str, Enum):
    user = "user"
