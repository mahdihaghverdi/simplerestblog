from enum import Enum, auto


class StrEnum(str, Enum):
    pass


class RoutesEnum(StrEnum):
    GET_BY_USERNAME = auto()


class UserRolesEnum(StrEnum):
    ADMIN = auto()
    USER = auto()


class PermissionGrantsEnum(StrEnum):
    IS_ALLOWED = auto()
    NOT_ALLOWED = auto()
    NOT_SELF_NOT_ALLOWED = auto()
