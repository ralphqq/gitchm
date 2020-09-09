"""
Some helper functions and classes used throughout the test suite

Constants:
    TEST_DIR
    COMMIT_DATAFILE
    DEST_REPO_PREFIX
    FEATURE_BRANCH
    DEST_MASTER_COMMITS
    DEST_FEATURE_COMMITS
    ITEM_OPS_RETURN_VALUE

Helper functions:
    load_iter_commits(repo, branch='master', mode='dict')
    load_commit_data()
    make_commits(repo, commits_data):
    read_gitchm(workdir)
    listify_attribute(seq, mode='obj')
    set_attr_or_key(seq, field, values)

Coroutines:
    run_mirror_ops(mirror, **kwargs)

Helper Classes:
    ModifiedCHM
"""
from datetime import datetime
import json
import os
from typing import Generator

from git import Actor, Commit, Repo

from gitchm.mirror import CommitHistoryMirror, GITCHMFILE


# Constants

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
COMMIT_DATAFILE = os.path.join(TEST_DIR, "data/commits.json")
DEST_REPO_PREFIX = "mirror"
FEATURE_BRANCH = "feature"
DEST_MASTER_COMMITS = 2  # no. of dummy commits in dest master
DEST_FEATURE_COMMITS = 4  # no. of dummy commits in dest feature
ITEM_OPS_RETURN_VALUE = "value"

# Helper functions


def load_iter_commits(
    repo: Repo, branch: str = "master", mode: str = "dict", **kwargs
) -> list:
    """Makes fetched Commit items ready to be used in `make_commits()`.

    This helper function converts the fetched Commits items into a list
    of dictionaries (similar to the output of `load_commit_data()`) or
    as a list of Commit objects.

    Args:
        repo (Repo): The repo to fetch commits from
        branch (str): The branch to fetch commits from (default
            is 'master')
        mode (str): Can either be 'dict' or 'obj':
            - 'dict' (default): returns results as list of dicts
            - 'obj': returns results as list of Commit objects
        kwargs: optional params for filtering commits
    """
    if mode not in ["obj", "dict"]:
        raise ValueError("mode must be obj or dict")

    if kwargs:
        kwargs.update({"regexp_ignore_case": True})

    commits = repo.iter_commits(branch, **kwargs)
    data = []
    for commit in commits:
        item = commit
        if mode == "dict":
            item = dict()
            item["hexsha"] = commit.hexsha
            item["message"] = commit.message
            item["timestamp"] = commit.committed_date
            item["author_name"] = commit.author.name
            item["author_email"] = commit.author.email
            item["committer_name"] = commit.committer.name
            item["committer_email"] = commit.committer.email
        data.append(item)
    return data


def load_commit_data() -> list:
    """Loads dummy commits data from JSON file."""
    commits_fetched = []

    # Load data for creating dummy commits
    with open(COMMIT_DATAFILE, "r", encoding="utf-8") as f:
        commits_fetched = json.load(f)

    # Sort in chronological order
    commits_fetched = sorted(commits_fetched, key=lambda x: x["timestamp"])

    return commits_fetched


def make_commits(
    repo: Repo, commits_data: list, has_mirror: bool = False
) -> list:
    """Loads commit data from JSON file and makes commits in given repo.

    Args:
        repo (`Repo`): git repo instance where commits will be made
        commits_data (list): Contains the commit details to write
        has_mirror (bool): Indicates whether to write to `.gitchmirror`

    Returns:
        list: list of dicts representing commits made
    """
    # Simulate git add-commit workflow for each commit item
    for i, commit_item in enumerate(commits_data):
        changes = []
        hexsha = commit_item["hexsha"]
        message = commit_item["message"]
        commit_dt = datetime.fromtimestamp(
            commit_item["timestamp"]
        ).isoformat()

        # Create new file
        fname = f"{i:05d}.txt"
        fpath = os.path.join(repo.working_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            # Write commit message as file content
            f.write(message)
        changes.append(fpath)

        # Write to .gitchmirror file
        if has_mirror:
            gpath = os.path.join(repo.working_dir, GITCHMFILE)
            with open(gpath, "a+", encoding="utf-8") as g:
                g.write(f"{hexsha}\n")
            changes.append(gpath)

        # Create author and committer
        author = Actor(
            name=commit_item["author_name"], email=commit_item["author_email"]
        )
        committer = Actor(
            name=commit_item["committer_name"],
            email=commit_item["committer_email"],
        )

        # Stage and commit the created file(s)
        repo.index.add(changes)
        repo.index.commit(
            message=message,
            author=author,
            author_date=commit_dt,
            committer=committer,
            commit_date=commit_dt,
        )

    return commits_data


def read_gitchm(workdir: str) -> list:
    """Returns contents of `.gitchmirror` as list."""
    data = []
    with open(os.path.join(workdir, GITCHMFILE)) as f:
        data = f.read().splitlines()
    return data


def listify_attribute(seq: list, attr: str, mode: str = "obj") -> list:
    """Returns list of values specified by attribute or dict key."""
    if mode not in ["obj", "dict"]:
        raise ValueError("mode must be obj or dict")

    if mode == "obj":
        return [getattr(p, attr) for p in seq]
    elif mode == "dict":
        return [p.get(attr) for p in seq]


def set_attr_or_key(seq: list, field: str, values: list) -> None:
    """Sets value to the given attribute or key for each item in `seq`.

    If the items are dicts, the function assigns given values to the
    specified key of each item. Otherwise, the values are assigned
    to the given attribute of each object.

    Args:
        seq (list): The list of dictionaries or objects
        field (str): The name of the key or attribute to be modified
        values (list): The list of values to be assigned; must be of the
            same length as `seq`, and each item in `values` must
            exactly correspond to an item in `seq` (i.e.,the  item at
            index n of `values` should correspond to the item at
            index n of `seq`)
    """
    for item, val in zip(seq, values):
        if isinstance(item, dict):
            item[field] = val
        else:
            setattr(item, field, val)


# Coroutines


async def run_mirror_ops(mirror: CommitHistoryMirror, **kwargs) -> None:
    """Runs `mirror.reflect()` with given kwargs."""
    await mirror.reflect(**kwargs)


# Helper classes


class ModifiedCHM(CommitHistoryMirror):
    """Overrides parent class's __init__ method.

    This makes it possible to separately test each
    method called in the original class's __init__ method.
    """

    def __init__(
        self,
        source_workdir: str = "",
        dest_workdir: str = "",
        prefix: str = DEST_REPO_PREFIX,
    ) -> None:
        self.source_workdir = source_workdir
        self.dest_workdir = dest_workdir
        self.dest_prefix = prefix
        self.prior_dest_exists = False
        self.dest_head_commit = None
        self.dest_has_tree = False
        self.dest_commit_hashes = []
        self.dest_is_mirror = False
