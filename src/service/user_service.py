from src.core.exceptions import DuplicateUsernameError
from src.core.schemas import UserSignupSchema, UserSchema
from src.core.security import hash_password
from src.repository.user_repo import UserRepo
from src.service import Service


class UserService(Service[UserRepo]):
    async def signup_user(self, user_data: UserSignupSchema) -> UserSchema:
        user_data.password = hash_password(user_data.password)
        if user_data.telegram is not None:
            user_data.telegram = f"https://t.me/{user_data.telegram}"
        if user_data.instagram is not None:
            user_data.instagram = f"https://instagram.com/{user_data.instagram}"
        if user_data.twitter is not None:
            user_data.twitter = f"https://x.com/@{user_data.twitter}"

        user = await self.repo.add(user_data)
        if user is None:
            raise DuplicateUsernameError(user_data.username)
        return user
