import logging
import os

from git import Repo
from git.exc import InvalidGitRepositoryError


from app.utils import create_dir, git_repo_exceptions


DEST_REPO_PREFIX = 'mirror'

logger = logging.getLogger()


class CommitHistoryMirror:

    def __init__(self, source_workdir: str, dest_workdir: str = '') -> None:
        self.source_workdir = source_workdir
        self._init_source_repo()
        self.dest_exists = False    # True if `dest_workdir` is given

        if not dest_workdir:
            self._init_empty_dest_repo()
        else:
            # Make sure source and destination directories are not the same 
            # before calling repo initialization
            if source_workdir == dest_workdir:
                raise ValueError(
                    'Source repo must not be the same as destination repo'
                )
            self.dest_exists = True
            self._init_existing_dest_repo(dest_workdir)

    @git_repo_exceptions
    def _init_source_repo(self) -> None:
        """Accesses git repo located in `self.source_workdir`."""
        self.parent_dir, self.source_repo_name = os.path.split(
            self.source_workdir
        )
        self.source_repo = Repo(self.source_workdir)

    @git_repo_exceptions
    def _init_empty_dest_repo(self) -> None:
        """Creates and initializes empty destination repo."""
        # Create the destination workdir
        dest_repo_name = f'{DEST_REPO_PREFIX}-{self.source_repo_name}'
        self.dest_workdir = create_dir(
            full_path=os.path.join(
                self.parent_dir,
                dest_repo_name
            ),
            on_conflict='resolve'
        )

        # Get dest repo name (to get modified name, as appropriate)
        self.dest_repo_name = os.path.split(self.dest_workdir)[-1]

        # Initialize empty git repo
        self.dest_repo = Repo.init(self.dest_workdir)

    @git_repo_exceptions
    def _init_existing_dest_repo(self, dest_workdir: str) -> None:
        """Initializes existing destination repo."""
        self.dest_workdir = dest_workdir
        try:
            # Try if the path points to a valid git repo
            self.dest_repo = Repo(dest_workdir)
            logger.info(f'Directory {dest_workdir} is a valid git repo.')
        except InvalidGitRepositoryError:
            # Initialize dir as git repo
            logger.info(
                f'Directory {dest_workdir} is not a git repo. '
                f'Initializing it as a repository'
            )
            self.dest_repo = Repo.init(dest_workdir)
