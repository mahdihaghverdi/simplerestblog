from typing import TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import PermissionGrantsEnum, RoutesEnum, UserRolesEnum
from src.core.exceptions import UnAuthorisedAccessError
from src.core.schemas import UserSchema
from src.repository.unitofwork import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService


async def _is_allowed(*_, **__):
    return True


async def _not_allowed(*_, **__):
    return False


async def _not_self_not_allowed(
    username: str,
    requested_user: UserSchema,
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


async def check_permission(
    db: AsyncSession,
    user_role: UserRolesEnum,
    username: str,
    user: UserSchema,
    route: RoutesEnum,
    permission_setting: ACLSetting,
):
    async with UnitOfWork(db):
        repo = UserRepo(db)
        service = UserService(repo)
        await service.get_user(username)

    not_allowed = _GRANT_MAPPER[PermissionGrantsEnum.NOT_ALLOWED]
    try:
        permission_for_endpoint = permission_setting[route]
        grant = permission_for_endpoint[user_role]
    except KeyError:
        await not_allowed()
    else:
        func = _GRANT_MAPPER[grant]
        await func(username, user)
