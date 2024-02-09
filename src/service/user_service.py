from zoneinfo import ZoneInfo

from src.core.exceptions import DuplicateUsernameError
from src.core.schemas import UserSignupSchema, UserSchema
from src.core.security import hash_password
from src.repository.user_repo import UserRepo
from src.service import Service


class UserService(Service[UserRepo]):
    async def signup_user(self, user_data: UserSignupSchema) -> UserSchema:
        user_data.password = hash_password(user_data.password)
        user = await self.repo.add(user_data)
        if user is None:
            raise DuplicateUsernameError(user_data.username)
        user.created = user.created.astimezone(ZoneInfo("Asia/Tehran"))
        if user.telegram is not None:
            user.telegram = f"https://t.me/{user.telegram}"
        if user.instagram is not None:
            user.instagram = f"https://instagram.com/{user.instagram}"
        if user.twitter is not None:
            user.twitter = f"https://x.com/@{user.twitter}"
        return user
