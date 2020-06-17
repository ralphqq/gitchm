import logging
import os

from git import Repo

from app.utils import create_dir, git_repo_exceptions


DEST_REPO_PREFIX = 'mirror'

logger = logging.getLogger()


class CommitHistoryMirror:

    def __init__(self, source_workdir: str, dest_workdir: str = '') -> None:
        self.source_workdir = source_workdir
        self._init_source_repo()
        if not dest_workdir:
            self._init_empty_dest_repo()
        else:
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
        pass
