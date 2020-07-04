"""
Helper functions and utilities

Decorators:
    git_repo_exceptions()

Helper functions:
    create_dir(full_path)
    delete_dir(full_path)
    clean_dict(orig_dict)
    create_actor(name, email)
    to_datetime(date_str, output='dt')
    format_stats(stats)
"""
from datetime import datetime
import functools
import logging
import os
import shutil
from typing import Union

from git import Actor
from git.exc import GitError
from dateutil.parser import parse

from gitchm.exc import IncompleteCommitDetails


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


def create_actor(name: str = '', email: str = '') -> Actor:
    """Creates an instance of `Actor` class.

    Raises:
        IncompleteCommitDetails: if both `name` and `email` are empty
    """
    if not name and not email:
        raise IncompleteCommitDetails(
            'Cannot create author/committer: No name or email provided'
        )
    return Actor(name=name, email=email)


def to_datetime(text: str, output: str = 'dt') -> Union[datetime, int]:
    """Converts str into datetime or timestamp.

    Args:
        text (str): The date/time string to convert
        output (str): Indicates whether to return the result as 
            datetime object or as Unix timestamp
    """
    if output not in ['dt', 'ts']:
        raise ValueError("`output` can only be 'dt' or 'ts'")

    try:
        result = parse(text)
        if output == 'ts':
            result = result.timestamp()
        return result

    except Exception as e:
        raise ValueError(
            f"Unable to convert string '{text}' "
            f"into datetime or timestamp: {e}"
        )


def format_stats(stats: dict) -> str:
    """Prepares stats for logging."""
    return ', '.join([f'{k}: {v} commits' for k, v in stats.items()])
