"""
Helper functions and utilities

Decorators:
    git_repo_exceptions()

Helper functions:
    create_dir(full_path)
    delete_dir(full_path)
    clean_dict(orig_dict)
"""
from datetime import datetime
import functools
import logging
import os
import shutil

from git.exc import GitError


logger = logging.getLogger(__name__)

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

def create_dir(full_path: str, on_conflict: str = 'raise') -> str:
    """Creates directory in given path."""
    already_exists = os.path.exists(full_path)

    if already_exists:
        if on_conflict == 'raise':
            raise ValueError(f'{full_path} already exists.')
        elif on_conflict == 'replace':
            # Delete existing dir to be re-created later
            delete_dir(full_path)
        elif on_conflict == 'resolve':
            # Append a string to directory name
            # to make the name unique
            postfix = datetime.now().strftime('%Y%m%d%H%M%S')
            full_path = f'{full_path}-{postfix}'

    os.makedirs(full_path)
    return full_path


def delete_dir(full_path: str) -> None:
    """Deletes given path if it exists."""
    if os.path.exists(full_path):
        shutil.rmtree(full_path)


def clean_dict(orig_dict: dict) -> dict:
    """Removes items with null values from dict."""
    return {k: v for k, v in orig_dict.items() if v is not None}
