"""
Sub-classed GitError exceptions

Classes:
    IncompleteGitDetailsException
"""
from git.exc import GitError


class IncompleteGitDetailsException(GitError):
    """Raised when any crucial git commit detail is missing."""
    pass
