"""
Some helper functions and classes used throughout the test suite

Helper functions:
    make_commits(exclude_n_commits: int = 0) -> list:

Helper Classes:
    ModifiedCHM
"""
from datetime import datetime
import json
import os

from git import Actor, Repo

from app.mirror import CommitHistoryMirror


TEST_DIR = os.path.abspath(os.path.dirname(__file__))
COMMIT_DATAFILE = os.path.join(TEST_DIR, 'data/commits.json')
DEST_REPO_PREFIX = 'mirror'


# Helper functions

def make_commits(repo: Repo, exclude_commits: int = 0) -> list:
    """Loads commit data from JSON file and makes commits in given repo.

    Args:
        repo (`Repo`): git repo instance where commits will be made
        exclude_commits (int): number of latest commits to exclude

    Returns:
        list: list of dicts representing commits made
    """
    commits_fetched = []

    # Load data for creating dummy commits
    with open(COMMIT_DATAFILE, 'r', encoding='utf-8') as f:
        commits_fetched = json.load(f)

    # Sort in chronological order
    # and slice list based on excluded commits
    commits_fetched = sorted(commits_fetched, key=lambda x: x['timestamp'])
    commits_made = commits_fetched[:len(commits_fetched) - exclude_commits]

    # Simulate git add-commit workflow for each commit item
    for i, commit_item in enumerate(commits_made):
        message = commit_item['message']
        commit_dt = datetime.fromtimestamp(commit_item['timestamp']).isoformat()

        # Create new file
        fname = f'{i:05d}.txt'
        fpath = os.path.join(repo.working_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            # Write commit message as file content
            f.write(message)

        # Create author and committer
        author = Actor(
            name=commit_item['author_name'],
            email=commit_item['author_email']
        )
        committer = Actor(
            name=commit_item['committer_name'],
            email=commit_item['committer_email']
        )

        # Stage and commit the created file
        repo.index.add([fpath])
        repo.index.commit(
            message=message,
            author=author,
            author_date=commit_dt,
            committer=committer,
            commit_date=commit_dt
        )

    return commits_made


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
