from enum import Enum

class AccountRole(Enum):
    PUBLIC = "public"
    OPERATOR = "operator"
    ADMIN = "admin"