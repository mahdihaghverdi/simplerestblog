from enum import Enum


class StrEnum(str, Enum):
    pass


class RoutesEnum(StrEnum):
    GET_BY_USERNAME = "GET_BY_USERNAME"


class UserRolesEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class PermissionGrantsEnum(StrEnum):
    IS_ALLOWED = "IS_ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
    NOT_SELF_NOT_ALLOWED = "NOT_SELF_NOT_ALLOWED"
