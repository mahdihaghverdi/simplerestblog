from typing import TypeVar, Generic

R = TypeVar("R")


class Service(Generic[R]):
    def __init__(self, repo: R):
        self.repo: R = repo
