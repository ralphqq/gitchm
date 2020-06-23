"""
Some helper functions and classes used throughout the test suite

Constants:
    TEST_DIR
    COMMIT_DATAFILE
    DEST_REPO_PREFIX
    FEATURE_BRANCH

Helper functions:
    load_commit_data()
    make_commits(repo, commits_data):

Helper Classes:
    ModifiedCHM
"""
from datetime import datetime
import json
import os

from git import Actor, Repo

from app.mirror import CommitHistoryMirror, GITCHMFILE


# Constants

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
COMMIT_DATAFILE = os.path.join(TEST_DIR, 'data/commits.json')
DEST_REPO_PREFIX = 'mirror'
FEATURE_BRANCH = 'feature'


# Helper functions

def load_commit_data() -> list:
    """Loads dummy commits data from JSON file."""
    commits_fetched = []

    # Load data for creating dummy commits
    with open(COMMIT_DATAFILE, 'r', encoding='utf-8') as f:
        commits_fetched = json.load(f)

    # Sort in chronological order
    commits_fetched = sorted(commits_fetched, key=lambda x: x['timestamp'])

    return commits_fetched


def make_commits(
        repo: Repo,
        commits_data: list,
        has_mirror: bool = False
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
        hexsha = commit_item['hexsha']
        message = commit_item['message']
        commit_dt = datetime.fromtimestamp(commit_item['timestamp']).isoformat()

        # Create new file
        fname = f'{i:05d}.txt'
        fpath = os.path.join(repo.working_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            # Write commit message as file content
            f.write(message)
        changes.append(fpath)

        # Write to .gitchmirror file
        if has_mirror:
            gpath = os.path.join(repo.working_dir, GITCHMFILE)
            with open(gpath, 'a+', encoding='utf-8') as g:
                g.write(f'{hexsha}\n')
            changes.append(gpath)

        # Create author and committer
        author = Actor(
            name=commit_item['author_name'],
            email=commit_item['author_email']
        )
        committer = Actor(
            name=commit_item['committer_name'],
            email=commit_item['committer_email']
        )

        # Stage and commit the created file(s)
        repo.index.add(changes)
        repo.index.commit(
            message=message,
            author=author,
            author_date=commit_dt,
            committer=committer,
            commit_date=commit_dt
        )

    return commits_data


# Helper classes

class ModifiedCHM(CommitHistoryMirror):
    """Overrides parent class's __init__ method.

    This makes it possible to separately test each 
    method called in the original class's __init__ method.
    """

    def __init__(
            self,
            source_workdir: str = '',
            dest_workdir: str = '',
            prefix: str = DEST_REPO_PREFIX
        ) -> None:
        self.source_workdir = source_workdir
        self.dest_workdir = dest_workdir
        self.dest_prefix = prefix
        self.prior_dest_exists = False
        self.dest_head_commit = None
        self.dest_has_tree = False
        self.dest_commit_hashes = []
        self.dest_is_mirror = False
