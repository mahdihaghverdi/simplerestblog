class DuplicateUsernameError(Exception):
    def __init__(self, username):
        self.message = f"username: {username!r} already exists!"

    def __str__(self):
        return self.message


class UnAuthorizedError(Exception):
    message: str = "Unauthorized Access!"


class CredentialsError(UnAuthorizedError):
    message = "Could not validate credentials"


class UnAuthorisedAccessError(UnAuthorizedError):
    message = "Invalid access. You are not allowed to access this route"
