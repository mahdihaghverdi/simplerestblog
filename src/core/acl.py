from typing import Annotated, TypeAlias
from collections.abc import Callable

from fastapi import Depends

from src.core.enums import PermissionGrantsEnum, RoutesEnum, UserRolesEnum
from src.core.exceptions import UnAuthorisedAccessError
from src.core.schemas import UserSchema
from src.service.user_service import get_user


async def _is_allowed(*_, **__):
    return True


async def _not_allowed(*_, **__):
    return False


async def _not_self_not_allowed(
    username: str,
    requested_user: Annotated[UserSchema, Depends(get_user)],
) -> bool:
    if username == requested_user.username:
        return True
    raise UnAuthorisedAccessError()


_GRANT_MAPPER = {
    PermissionGrantsEnum.IS_ALLOWED: _is_allowed,
    PermissionGrantsEnum.NOT_ALLOWED: _not_allowed,
    PermissionGrantsEnum.NOT_SELF_NOT_ALLOWED: _not_self_not_allowed,
}

ACLSetting: TypeAlias = dict[RoutesEnum, dict[UserRolesEnum, PermissionGrantsEnum]]
_ACL_MAPPER: ACLSetting = {
    RoutesEnum.GET_BY_USERNAME: {
        UserRolesEnum.ADMIN: PermissionGrantsEnum.IS_ALLOWED,
        UserRolesEnum.USER: PermissionGrantsEnum.NOT_SELF_NOT_ALLOWED,
    },
}


def get_permission_setting():
    return _ACL_MAPPER


async def _check_permission(
    user_role: UserRolesEnum,
    username: str,
    route: RoutesEnum,
    permission_setting: ACLSetting,
):
    not_allowed = _GRANT_MAPPER[PermissionGrantsEnum.NOT_ALLOWED]
    try:
        permission_for_endpoint = permission_setting[route]
        grant = permission_for_endpoint[user_role]
    except KeyError:
        await not_allowed()
    else:
        func = _GRANT_MAPPER[grant]
        await func(username)


async def get_permission_callable() -> Callable:
    return _check_permission
