import functools
import logging

from git.exc import GitError


logger = logging.getLogger()

# Decorators

def git_repo_exceptions(func):
    """Handles GitPython exceptions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GitError as e:
            logger.error(f'Git error in {func.__name__}: {e}')
            raise e
    return wrapper
