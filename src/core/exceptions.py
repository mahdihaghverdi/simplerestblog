from http import HTTPStatus


class Error(Exception):
    code: int
    code_message: str

    def __init__(self, message=None):
        self.message = message


class ResourceNotFoundError(Error):
    code = HTTPStatus.NOT_FOUND.value
    code_message = HTTPStatus.NOT_FOUND.description


class UserNotFoundError(ResourceNotFoundError):
    def __init__(self, username):
        self.message = f"<User:{username!r}> is not found!"


class DraftNotFoundError(ResourceNotFoundError):
    def __init__(self, draft_id):
        self.message = f"<Draft:{draft_id!r}> is not found!"


class PostNotFoundError(ResourceNotFoundError):
    def __init__(self, link):
        self.message = f"<Post:{link!r} is not found!"


class CommentNotFoundError(ResourceNotFoundError):
    def __init__(self, comment_id):
        self.message = f"<Comment:{comment_id} is not found!"


class BadRequestError(Error):
    code = HTTPStatus.BAD_REQUEST.value
    code_message = HTTPStatus.BAD_REQUEST.description


class DuplicateUsernameError(BadRequestError):
    def __init__(self, username):
        self.message = f"username: {username!r} already exists!"


class DraftPublishedBeforeError(BadRequestError):
    def __init__(self, draft_id):
        self.message = f"<Draft:{draft_id}> is published before!"


class UnAuthorizedError(Error):
    code = HTTPStatus.UNAUTHORIZED.value
    code_message = HTTPStatus.UNAUTHORIZED.description


class CredentialsError(UnAuthorizedError):
    def __init__(self, message="Could not validate credentials"):
        self.message = message


class UnAuthorisedAccessError(UnAuthorizedError):
    message = "Invalid access. You are not allowed to access this route"


class InternalServerError(Error):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    code_message = HTTPStatus.INTERNAL_SERVER_ERROR.description


class DatabaseError(InternalServerError):
    pass


class DatabaseIntegrityError(DatabaseError):
    pass


class DatabaseConnectionError(DatabaseError):
    pass


class ForbiddenError(Error):
    code = HTTPStatus.FORBIDDEN
    code_message = HTTPStatus.FORBIDDEN.description
