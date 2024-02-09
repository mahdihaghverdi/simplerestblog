class DuplicateUsernameError(Exception):
    def __init__(self, username):
        self.message = f"username: {username!r} already exists!"

    def __str__(self):
        return self.message


class UnAuthorizedError(Exception):
    pass


class UnAuthorizedLoginError(UnAuthorizedError):
    pass


class CredentialsException(UnAuthorizedError):
    pass
