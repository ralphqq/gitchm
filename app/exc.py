"""
Sub-classed GitError exceptions and other errors used 
in the code

Classes:
    IncompleteCommitDetails
    ValidationError
    TransformationError
"""
from git.exc import GitError


class IncompleteCommitDetails(GitError):
    """Raised when any crucial git commit detail is missing."""
    pass


class ValidationError(ValueError):
    """Thrown when encountering invalid user input."""
    pass


class TransformationError(ValueError):
    """Raised anytime user input fails to get transformed."""
    pass
