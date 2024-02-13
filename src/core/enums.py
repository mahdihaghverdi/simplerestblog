from enum import Enum


class StrEnum(str, Enum):
    pass


class RoutesEnum(StrEnum):
    GET_USER_BY_USERNAME = "GET_USER_BY_USERNAME"
    GET_ALL_DRAFTS_BY_USERNAME = "GET_ALL_DRAFTS_BY_USERNAME"
    GET_ONE_DRAFT_BY_USERNAME = "GET_ONE_DRAFT_BY_USERNAME"


class UserRolesEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class PermissionGrantsEnum(StrEnum):
    IS_ALLOWED = "IS_ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
    NOT_SELF_NOT_ALLOWED = "NOT_SELF_NOT_ALLOWED"
