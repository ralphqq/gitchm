"""
Sub-classed GitError exceptions

Classes:
    IncompleteCommitDetails
"""
from git.exc import GitError


class IncompleteCommitDetails(GitError):
    """Raised when any crucial git commit detail is missing."""
    pass
