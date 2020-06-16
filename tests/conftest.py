from datetime import datetime
import json
import os
import tempfile

from git import Actor, Repo
import pytest

from app.utils import create_dir, delete_dir


TEST_DIR = os.path.abspath(os.path.dirname(__file__))
COMMIT_DATAFILE = os.path.join(TEST_DIR, 'data/commits.json')
PARENT_DIR = 'chm-test-session'
SOURCE_WORKDIR = 'project-src'


@pytest.fixture(scope='session')
def init_chm_test_session():
    """Creates and removes the main directory for the test session."""
    tmp_dir = tempfile.gettempdir()
    
    # Create the main directory
    parent_dir_path = create_dir(
        full_path=os.path.join(tmp_dir, PARENT_DIR),
        on_conflict='replace'
    )
    yield parent_dir_path

    # Delete the entire main directory
    delete_dir(parent_dir_path)


@pytest.fixture(scope='module')
def init_source_repo(init_chm_test_session):
    """Sets up and tears down a non-bare git repo.

    Yields:
        tuple: (
            source_workdir_path,
            parent_dir_path,
            commits_from_json,
        
    """
    parent_dir_path = init_chm_test_session

    # Create source workdir
    source_workdir_path = create_dir(
        full_path=os.path.join(parent_dir_path, SOURCE_WORKDIR),
        on_conflict='replace'
    )

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
        commit_dt = datetime.fromtimestamp(commit_item['timestamp']).isoformat()

        # Create new file
        fname = f'{i:05d}.txt'
        fpath = os.path.join(source_workdir_path, fname)
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

    yield (
        source_workdir_path,
        parent_dir_path,
        commits,
    )

    # Delete the source repo directory
    delete_dir(source_workdir_path)
