import asyncio
from collections import defaultdict
from datetime import datetime
import logging
import os
from typing import Generator, Union

from git import Commit, Repo
from git.exc import InvalidGitRepositoryError

from gitchm.utils import (
    clean_dict,
    create_dir,
    git_repo_exceptions,
)


logger = logging.getLogger(__name__)

GITCHMFILE = '.gitchmirror'
SUMMARYFILE = 'summary.txt'

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
        self.stats = defaultdict(lambda: 0)

        self._init_source_repo()

        # True if `dest_workdir` points to existing repo
        self.prior_dest_exists = False

        # The current head in the active dest repo branch
        self.dest_head_commit = None

        # Indicates whether dest has valid tree heads
        self.dest_has_tree = False

        # list of commit hashes reflected in  the active dest branch
        # non-empty only if dest is a mirror repo
        self.dest_commit_hashes = []

        # Indicates whether dest repo is a mirror repo or not
        self.dest_is_mirror = False

        if not dest_workdir:
            self._init_empty_dest_repo()
            
        else:
            # Make sure source and destination directories are not the same 
            # before calling repo initialization
            if source_workdir == dest_workdir:
                raise ValueError(
                    'Source repo must not be the same as destination repo'
                )

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

            self.prior_dest_exists = True
            self._check_tree_state()

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

    def _check_tree_state(self):
        """Determines if destination repo has working tree head."""
        logger.debug('Checking if destination has working tree head')

        if self.dest_repo.heads:
            logger.info('Detected working tree head in destination')
            self.dest_has_tree = True
        else:
            logger.info('Destination has no working tree')

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
                `source_branch`; but this can only be set if the 
                destination repo has an identifiable working tree head

            Raises:
                ValueError: if `dest_branch` is specified in a 
                    destination repo which does not have any working 
                    tree heads
        """
        if not self.dest_has_tree and dest_branch:
            # Cannot set active branch in a destination repo
            #  which does not have any working tree heads
            raise ValueError(
                f'Destination repo currently does not have a '
                'working tree head; cannot set target branch'
            )

        logger.debug('Preparing to replicate commits')

        try:
            # Check if dest repo has tree head
            if self.dest_has_tree:
                    # Set active branch in dest repo
                    # and get head commit
                dest_branch = dest_branch if dest_branch else source_branch
                self._set_active_dest_branch(dest_branch)
                self.dest_head_commit = self.dest_repo.head.commit
                self._check_mirror_state()

            # Set up git-rev-list-options
            options = clean_dict({
                'rev': source_branch,
                'author': author or None,
                'committer': committer or None,
                'before': before or None,
                'after': after or None,
                'regexp_ignore_case': True,
            })

            logger.debug(
                f'Fetching commits from source repo using options {options}'
            )
            commits = self.source_repo.iter_commits(**options)
            await self._replicate(commits)

        except Exception as e:
            logger.error(
                f'Unhandled error during commit history replication: {e}'
            )

    async def _replicate(
            self,
            commits: Generator[Commit, None, None]
        ) -> None:
        """Wraps replication as async tasks and runs them in parallel."""
        logger.debug('Preparing commit replication tasks')
        tasks = [
            self._commit(i, commit) for i, commit in enumerate(commits)
        ]
        task_count = len(tasks)
        self.stats['found'] = task_count

        if task_count:
            logger.info(
                f'Found {task_count} commits that matched specified options'
            )
            for coro in asyncio.as_completed(tasks):
                result = await coro
                self.stats[result] += 1
                self.stats['processed'] += 1

            logger.info(
                f"Processed {self.stats['processed']} of {task_count} commits"
            )
        else:
            logger.info('No commits found that matched the provided options')

        logger.debug('Closing replication process')

    async def _commit(self, n: int, commit_item: Commit) -> str:
        """Makes the commit into the destination repo.

        Returns:
            str: short text describing commit outcome, can be one of:
                - 'replicated'
                - 'skipped'
                - 'failed'
        """
        m = n + 1

        logger.debug(f'Processing commit #{m}')
        hexsha = commit_item.hexsha
        if hexsha in self.dest_commit_hashes:
            logger.debug(f'{hexsha} already mirrored, skipping commit #{m}')
            return 'skipped'

        try:
            message = commit_item.message
            committed_ts = commit_item.committed_date
            committed_dt = datetime.fromtimestamp(committed_ts).isoformat()

            workdir = self.dest_repo.working_dir
            fpath = os.path.join(workdir, SUMMARYFILE)
            gpath = os.path.join(workdir, GITCHMFILE)
            with open(fpath, 'a+') as fh, open(gpath, 'a+') as gh:
                fh.write(f'{message}\n')
                gh.write(f'{hexsha}\n')

            self.dest_repo.index.add([fpath, gpath])
            self.dest_repo.index.commit(
                message=message,
                author=commit_item.author,
                author_date=committed_dt,
            committer=commit_item.committer,
            commit_date=committed_dt
            )

        except Exception as e:
            logger.error(f'Error while replicating commit #{m}: {e}')
            return 'failed'

        else:
            logger.debug(f'Successfully replicated commit #{m}')
            return 'replicated'

    def _set_active_dest_branch(self, dest_branch: str) -> None:
        """Sets active branch in destination repo."""
        logger.debug(f'Switching to branch {dest_branch} in destination repo')
        if self.dest_repo.active_branch.name == dest_branch:
            # Target branch is already active
            logger.info(f'{dest_branch} is already the active branch')
            return None

        branch_type = 'existing'
        for branch in self.dest_repo.branches:
            if branch.name == dest_branch:
                logger.debug(f'Found existing branch {dest_branch}')
                branch.checkout()
                break

        else:   # same level as for loop
            # Target branch is new, so create it
            # before checking it out
            self.dest_repo.heads.master.checkout(b=dest_branch)
            logger.debug(f'Created new branch {dest_branch}')
            branch_type = 'new'

        logger.info(
            f'Switched to {branch_type} branch '
            f'{dest_branch} in destination repo'
        )

    def _get_commit_hashes(
        self,
        repo_name: str,
        branch: str = 'master'
    ) -> list:
        """Returns list of commit hashes (hex SHA) in branch.

        Args:
            repo_name (str): Can either be 'source' or 'dest'
            branch (str): Name of branch in repo, defaults to 'master'

        Raises:
            ValueError: if `repo_name` is neither 'source' nor 'dest'
        """
        logger.debug(
            f'Checking existing commits in {branch} of {repo_name} repo'
        )
        repo = None

        if repo_name.lower() in ['source', 'src']:
            repo = self.source_repo
        elif repo_name.lower() in ['destination', 'dest']:
            repo = self.dest_repo
        else:
            raise ValueError(
                "Value for `repo_name` must be 'source' or 'dest'"
            )

        commits = [c.hexsha for c in repo.iter_commits(branch)]
        logger.info(
            f'Found {len(commits)} existing commits in '
            f'branch {branch} of {repo.working_dir}'
        )
        return commits

    def _check_mirror_state(self):
        """Reads contents of `.gitchmirror` file if available.

        Raises:
            ValueError: if destination repo has no working tree
        """
        if not self.dest_has_tree:
            raise ValueError('Destination has no working tree')

        logger.debug(f'Checking mirror status of destination repo')
        fpath = os.path.join(self.dest_repo.working_dir, GITCHMFILE)

        if os.path.exists(fpath):
            self.dest_is_mirror = True
            logger.info('Detected destination is a mirror repo')

            with open(fpath, 'r', encoding='utf-8') as f:
                self.dest_commit_hashes = f.read().splitlines()

            logger.info(
                f'Found {len(self.dest_commit_hashes)} '
                f'mirrored commits in destination'
            )

        else:
            logger.info('Destination is not a mirror repo yet')
