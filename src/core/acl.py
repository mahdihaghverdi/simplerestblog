from typing import TypeAlias

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import PermissionGrantsEnum, RoutesEnum, UserRolesEnum
from src.core.exceptions import UnAuthorisedAccessError
from src.repository.models import DraftModel, CommentModel
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService


async def _is_allowed(*_, **__):
    return True


async def _not_allowed(*_, **__):
    return False


async def _user_not_self_not_allowed(
    username: str,
    req_username: int | str,
    *args,
) -> bool:
    """Allow if the user is requested for him/herself resource"""
    if username == req_username:
        return True
    raise UnAuthorisedAccessError()


async def _draft_not_self_not_allowed(
    username: str, draft_id: int | str, session: AsyncSession
) -> bool:
    stmt = (
        select(DraftModel.id)
        .where(DraftModel.username == username)
        .where(DraftModel.id == draft_id)
    )
    draft = (await session.execute(stmt)).first()
    if draft is not None:
        return True
    raise UnAuthorisedAccessError()


async def _comment_not_self_not_allowed(
    username: str, comment_id: int | str, session: AsyncSession
) -> bool:
    stmt = (
        select(CommentModel.id)
        .where(CommentModel.username == username)
        .where(CommentModel.id == comment_id)
    )
    comment = (await session.execute(stmt)).first()
    if comment is not None:
        return True
    raise UnAuthorisedAccessError()


_GRANT_MAPPER = {
    PermissionGrantsEnum.IS_ALLOWED: _is_allowed,
    PermissionGrantsEnum.NOT_ALLOWED: _not_allowed,
    PermissionGrantsEnum.USER_NOT_SELF_NOT_ALLOWED: _user_not_self_not_allowed,
    PermissionGrantsEnum.DRAFT_NOT_SELF_NOT_ALLOWED: _draft_not_self_not_allowed,
    PermissionGrantsEnum.COMMENT_NOT_SELF_NOT_ALLOWED: _comment_not_self_not_allowed,
}

ACLSetting: TypeAlias = dict[RoutesEnum, dict[UserRolesEnum, PermissionGrantsEnum]]
_ACL_MAPPER: ACLSetting = {
    RoutesEnum.GET_USER_BY_USERNAME: {
        UserRolesEnum.ADMIN: PermissionGrantsEnum.IS_ALLOWED,
        UserRolesEnum.USER: PermissionGrantsEnum.USER_NOT_SELF_NOT_ALLOWED,
    },
    RoutesEnum.GET_ALL_DRAFTS_BY_USERNAME: {
        UserRolesEnum.ADMIN: PermissionGrantsEnum.IS_ALLOWED,
        UserRolesEnum.USER: PermissionGrantsEnum.USER_NOT_SELF_NOT_ALLOWED,
    },
    RoutesEnum.GET_ONE_DRAFT_BY_USERNAME: {
        UserRolesEnum.ADMIN: PermissionGrantsEnum.IS_ALLOWED,
        UserRolesEnum.USER: PermissionGrantsEnum.DRAFT_NOT_SELF_NOT_ALLOWED,
    },
    RoutesEnum.DELETE_COMMENT: {
        UserRolesEnum.ADMIN: PermissionGrantsEnum.IS_ALLOWED,
        UserRolesEnum.USER: PermissionGrantsEnum.COMMENT_NOT_SELF_NOT_ALLOWED,
    },
}


def get_permission_setting():
    return _ACL_MAPPER


async def check_permission(
    session: AsyncSession,
    user_role: UserRolesEnum,
    username: str,
    resource_identifier: str | int,
    route: RoutesEnum,
    permission_setting: ACLSetting,
):
    repo = UserRepo(session)
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
        await func(username, resource_identifier, session)
