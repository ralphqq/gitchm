import logging
import os

from git import Repo
from git.exc import InvalidGitRepositoryError


from app.utils import create_dir, git_repo_exceptions


logger = logging.getLogger(__name__)


class CommitHistoryMirror:

    def __init__(
            self,
            source_workdir: str,
            dest_workdir: str = '',
            prefix: dict = 'mirror'
        ) -> None:
        self.source_workdir = source_workdir
        self.dest_prefix = prefix
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

        logger.debug('Initialized mirror; mirror ready for use')

    @git_repo_exceptions
    def _init_source_repo(self) -> None:
        """Accesses git repo located in `self.source_workdir`."""
        logger.debug(f'Analyzing source directory {self.source_workdir}')
        self.parent_dir, self.source_repo_name = os.path.split(
            self.source_workdir
        )
        self.source_repo = Repo(self.source_workdir)
        logger.info(f'Detected source repo  {self.source_workdir}')

    @git_repo_exceptions
    def _init_empty_dest_repo(self) -> None:
        """Creates and initializes empty destination repo."""
        logger.debug('Creating new destination directory and repo')

        # Create the destination workdir
        dest_repo_name = f'{self.dest_prefix}-{self.source_repo_name}'
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
        logger.info(f'Initialized destination repo at {self.dest_workdir}')

    @git_repo_exceptions
    def _init_existing_dest_repo(self, dest_workdir: str) -> None:
        """Initializes existing destination repo."""
        logger.debug(f'Analyzing destination directory {dest_workdir}')
        self.dest_workdir = dest_workdir
        try:
            # Try if the path points to a valid git repo
            self.dest_repo = Repo(dest_workdir)
            logger.debug(f'Directory {dest_workdir} is a valid git repo.')
        except InvalidGitRepositoryError:
            # Initialize dir as git repo
            logger.debug(
                f'Directory {dest_workdir} is not a git repo. '
                f'Initializing it as a repository'
            )
            self.dest_repo = Repo.init(dest_workdir)
        logger.info(
            f'Initialized existing destination repo {self.dest_workdir}'
        )
