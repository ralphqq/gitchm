from datetime import datetime
import json
import os
import tempfile

from git import Actor, Repo
import pytest

from tests.utils import create_dir, delete_dir


TEST_DIR = os.path.abspath(os.path.dirname(__file__))
COMMIT_DATAFILE = os.path.join(TEST_DIR, 'data/commits.json')
PARENT_DIR = 'test-session'
SOURCE_WORKDIR = 'project-src'


@pytest.fixture(scope='session')
def source_repo():
    """Creates parent and working dirs then initializes a git repo."""
    # Create parent directory
    tmp_dir = tempfile.gettempdir()
    parent_dir_path = os.path.join(tmp_dir, PARENT_DIR)
    create_dir(parent_dir_path)

    # Create source workdir
    source_workdir_path = os.path.join(parent_dir_path, SOURCE_WORKDIR)
    create_dir(source_workdir_path, check_first=True)

    # Load data for creating dummy commits
    commits = []
    with open(COMMIT_DATAFILE, 'r', encoding='utf-8') as f:
        commits = json.load(f)

    # Sort in chronological order
    commits = sorted(commits, key=lambda x: x['timestamp'])

    # Create and initiallize source repo
    repo = Repo.init(source_workdir_path)

    # Simulate git add-commit workflow for each commit item
    for i, commit_item in enumerate(commits):
        message = commit_item['message']
        actor_email = commit_item['author']
        commit_dt = datetime.fromtimestamp(commit_item['timestamp']).isoformat()

        # Create new file
        fname = f'{i:05d}.txt'
        fpath = os.path.join(source_workdir_path, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            # Write commit message as file content
            f.write(message)

        # Create author and committer
        author = Actor(
            name='Author',
            email=actor_email
        )
        committer = Actor(
            name='Committer',
            email=actor_email
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

    yield source_workdir_path

    # Delete the test session directory
    delete_dir(parent_dir_path)
