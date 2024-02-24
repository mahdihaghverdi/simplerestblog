from enum import Enum


class StrEnum(str, Enum):
    pass


class RoutesEnum(StrEnum):
    GET_USER_BY_USERNAME = "GET_USER_BY_USERNAME"
    GET_ALL_DRAFTS_BY_USERNAME = "GET_ALL_DRAFTS_BY_USERNAME"
    GET_ONE_DRAFT_BY_USERNAME = "GET_ONE_DRAFT_BY_USERNAME"
    DELETE_COMMENT = "DELETE_COMMENT"


class APIPrefixesEnum(StrEnum):
    AUTH = "auth"
    USERS = "users"
    DRAFTS = "drafts"


class UserRolesEnum(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class PermissionGrantsEnum(StrEnum):
    IS_ALLOWED = "IS_ALLOWED"
    NOT_ALLOWED = "NOT_ALLOWED"
    USER_NOT_SELF_NOT_ALLOWED = "USER_NOT_SELF_NOT_ALLOWED"
    DRAFT_NOT_SELF_NOT_ALLOWED = "DRAFT_NOT_SELF_NOT_ALLOWED"
    COMMENT_NOT_SELF_NOT_ALLOWED = "COMMENT_NOT_SELF_NOT_ALLOWED"


class APIMethodsEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
