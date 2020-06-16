import logging
import os

from git import Repo

from app.utils import git_repo_exceptions


DEST_REPO_PREFIX = 'mirror'

logger = logging.getLogger()


class CommitHistoryMirror:

    def __init__(self, source_workdir: str) -> None:
        self.source_workdir = source_workdir
        self._init_source_repo()

    @git_repo_exceptions
    def _init_source_repo(self) -> None:
        """Accesses git repo located in `self.source_workdir`."""
        self.parent_dir, self.source_repo_name = os.path.split(
            self.source_workdir
        )
        self.source_repo = Repo(self.source_workdir)

    @git_repo_exceptions
    def _init_destination_repo(self) -> None:
        """Creates and initializes repo where history will be copied."""
        self.dest_repo_name = f'{DEST_REPO_PREFIX}-{self.source_repo_name}'
