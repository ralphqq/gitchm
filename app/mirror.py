import asyncio
import logging
import os
from typing import Generator, Union

from git import Commit, Repo
from git.exc import InvalidGitRepositoryError

from app.utils import (
    clean_dict,
    create_dir,
    git_repo_exceptions,
)


logger = logging.getLogger(__name__)


class CommitHistoryMirror:
    """Represents commit history mirroring session."""

    def __init__(
            self,
            source_workdir: str,
            dest_workdir: str = '',
            prefix: dict = 'mirror'
        ) -> None:
        """Sets up and initializes the mirror session.

        Args:
            source_workdir (str): Absolute path to the source repo
                dest_workdir (str): Absolute path to the destination 
                repo (optional); if not provided, the destination 
                working directory  will be automatically created
            prefix (str): The prefixof the automatically generated 
                destination working directory (defaults to 'mirror')

        Raises:
            ValueError: if source_workdir is the same as dest_workdir
        """
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

    async def reflect(
            self,
            author: str = '',
            committer: str = '',
            before: Union[int, str] = '',
            after: Union[int, str] = '',
            source_branch: str = 'master',
            dest_branch: str = ''
        ) -> None:
        """Executes the commit mirroring process.

        Args:
            author (str): Name or email address of author used to 
                filter commits (optional)
            committer (str): Name or email address of author used to 
                filter commits (optional)
            before (int or str): UNIX timestamp or date string; limits 
                commits older than given value (optional)
            after (int): UNIX timestamp or date string; limits 
                commits later than given value (optional)
            source_branch (str): The branch of the source repo to read 
                commits from; default is 'master'
            dest_branch (str: The branch in the destination repo where 
                the fetched commits will be replicated in; if not 
                provided, this will be set to the same branch as 
                `source_branch`
        """
        logger.debug('Preparing to replicate commits')

        try:
                # Set active branch in destination repo
            dest_branch = dest_branch if dest_branch else source_branch
            self._set_active_dest_branch(dest_branch)

            # Set up git-rev-list-options
            options = clean_dict({
                'rev': source_branch,
                'author': author or None,
                'committer': committer or None,
                'before': before or None,
                'after': after or None,
                'regexp_ignore_case': True,
            })

            logger.info(
                f'Fetching commits from source repo using options {options}'
            )
            commits = self.source_repo.iter_commits(**options)
            await self._replicate(commits)
            logger.info('Finished replicating commit history')

        except Exception as e:
            logger.error(
                f'Unhandled error during commit history replication: {e}'
            )

    async def _replicate(
            self,
            commits: Generator[Commit, None, None]
        ) -> None:
        """Wraps replication as async tasks and runs them in parallel."""
        tasks = [
            self._commit(i, commit) for i, commit in enumerate(commits)
        ]
        for coro in asyncio.as_completed(tasks):
            result = await coro

    async def _commit(self, n: int, commit_item: Commit) -> str:
        """Makes the commit into the destination repo.

        Returns:
            str: short text describing commit outcome, can be one of:
                - 'ok'
                - 'skipped'
                - 'error'
        """
        pass

    def _set_active_dest_branch(self, dest_branch: str) -> None:
        """Sets active branch in destination repo."""
        pass
