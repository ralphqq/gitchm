import logging
import os

from git import Repo


logger = logging.getLogger()


class CommitHistoryMirror:

    def __init__(self, source_workdir: str) -> None:
        self.source_workdir = source_workdir
        self.parent_dir, self.source_repo_name = os.path.split(source_workdir)
        self.source_repo = Repo(source_workdir)
