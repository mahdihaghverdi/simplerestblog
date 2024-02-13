from enum import Enum


class StrEnum(str, Enum):
    pass


class RoutesEnum(StrEnum):
    GET_BY_USERNAME = "GET_BY_USERNAME"
    CREATE_DRAFT = "CREATE_DRAFT"
    GET_ALL_DRAFTS = "GET_ALL_DRAFTS"
    GET_ONE_DRAFT = "GET_ONE_DRAFT"
    UPDATE_DRAFT = "UPDATE_DRAFT"
    DELETE_DRAFT = "DELETE_DRAFT"


class UserRolesEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class PermissionGrantsEnum(StrEnum):
    IS_ALLOWED = "IS_ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
    NOT_SELF_NOT_ALLOWED = "NOT_SELF_NOT_ALLOWED"
