class CommissionsEngineError(Exception):
    "A base exception for MLM Commissions Engine."


class MultipleRootsError(CommissionsEngineError):
    """Raises if multiple roots presented in partners hierarhy."""


class RootNotFoundError(CommissionsEngineError):
    """Raises if no root partner found."""


class ParentNotFoundError(CommissionsEngineError):
    """Raises if parent does not exist."""


class CycleError(CommissionsEngineError):
    """Raises if cycle detected in partners structure."""
