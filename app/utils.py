"""
Helper functions and utilities

Decorators:
    git_repo_exceptions()

Helper functions:
    create_dir(full_path)
    delete_dir(full_path)
"""
import functools
import logging
import os
import shutil

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


# Helper functions

def create_dir(full_path: str, check_first: bool = False) -> None:
    """Creates directory if it does not yet exist."""
    if check_first:
            # Delete existing dir first
            delete_dir(full_path)

    if not os.path.exists(full_path):
        os.makedirs(full_path)


def delete_dir(full_path: str) -> None:
    """Deletes given path if it exists."""
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
