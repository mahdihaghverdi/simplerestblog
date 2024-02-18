class ResourceNotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class UserNotFoundError(ResourceNotFoundError):
    def __init__(self, username):
        self.message = f"User {username!r} is not found!"


class DraftNotFoundError(ResourceNotFoundError):
    def __init__(self, draft_id):
        self.message = f"<Draft:{draft_id!r}> is not found!"


class PostNotFoundError(ResourceNotFoundError):
    def __init__(self, link):
        self.message = f"<Post:{link!r} is not found!"


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


class DraftPublishedBeforeError(Exception):
    def __init__(self, draft_id):
        self.message = f"<Draft:{draft_id}> is published before!"
