"""
Initializes CLI items and mirror settings
"""
import os

from gitchm.cli import ItemParser, PromptItem, PromptUI
from gitchm.utils import to_datetime


# Constants
INIT = 'init'
REFLECT = 'reflect'
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()


# Item parsers (validators and transformers)

path_parser = ItemParser(
    apply=lambda val: os.path.exists(val),
    error_msg='Path does not exist'
)

date_to_ts = ItemParser(
    apply=lambda val: int(to_datetime(val, output='ts')),
    error_msg='Unable to parse date/time value'
)


# Prompt items

## INIT options
source_workdir = PromptItem(
    name='source_workdir',
    message='Path to source repository (required):',
    is_required=True,
    group=INIT,
    validators=[path_parser]
)
dest_workdir = PromptItem(
    name='dest_workdir',
    message=(
        'Path to destination repository (optional, '
        'will be auto-generated if not provided):'
    ),
    group=INIT,
    active_on=source_workdir
)
prefix = PromptItem(
    name='prefix',
    message='Prefix to identify auto-generated destination directory (optional):',
    group=INIT,
    active_on=source_workdir,
    inactive_on=dest_workdir
)

## REFLECT options
author = PromptItem(
    name='author',
    message='Author name or email to query commits (optional)',
    active_on=source_workdir,
    group=REFLECT
)
committer = PromptItem(
    name='committer',
    message='Committer name or email to query commits (optional)',
    active_on=source_workdir,
    group=REFLECT
)
before = PromptItem(
    name='before',
    message='Query commits before date/time (yyyy-mm-dd HH:MM:SS, optional)',
    active_on=source_workdir,
    group=REFLECT,
    transformers=[date_to_ts]
)
after = PromptItem(
    name='after',
    message='Query commits after date/time (yyyy-mm-dd HH:MM:SS, optional)',
    active_on=source_workdir,
    group=REFLECT,
    transformers=[date_to_ts]
)
source_branch = PromptItem(
    name='source_branch',
    message=(
        'Branch in source repo to get commits from '
        '(optional, default is active branch):'
    ),
    active_on=source_workdir,
    group=REFLECT
)
dest_branch = PromptItem(
    name='dest_branch',
    message=(
        'Branch in destination repo to copy commits into '
        '(optional, default is active branch):'
    ),
    active_on=dest_workdir,
    group=REFLECT
)

PROMPT_ITEMS = [
    source_workdir,
    dest_workdir,
    prefix,
    author,
    committer,
    before,
    after,
    source_branch,
    dest_branch,
]

# Initialize a PromptUI instance
ui = PromptUI(prompt_items=PROMPT_ITEMS)
