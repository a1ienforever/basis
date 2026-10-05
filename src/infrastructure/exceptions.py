class InfrastructureError(Exception):
    """Base class for all infrastructure errors."""


class DatabaseRepositoryNotFoundError(InfrastructureError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Repository '{name}' is not registered in the unit of work")
        self.name = name
