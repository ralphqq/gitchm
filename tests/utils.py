from app.mirror import CommitHistoryMirror


class ModifiedCHM(CommitHistoryMirror):
    """Overrides parent class's __init__ method.

    This makes it possible to separately test each 
    method called in the original class's __init__ method.
    """

    def __init__(
            self,
            source_workdir: str = '',
            dest_workdir: str = ''
        ) -> None:
        self.source_workdir = source_workdir
        self.dest_workdir = dest_workdir
