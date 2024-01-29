from enum import Enum

class RetCode(Enum):
    OK = 0
    QUERY_FAILURE = 1
    INCORRECT_TARGET = 2
    NO_INVITER = 3