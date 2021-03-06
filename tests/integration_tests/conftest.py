import pytest

from gitchm.mirror import CommitHistoryMirror
from gitchm.utils import delete_dir
from tests.utils import run_mirror_ops


@pytest.fixture
def init_mirror(src_repo):
    async def _make_mirror(dest_workdir="", **kwargs):
        m = CommitHistoryMirror(
            source_workdir=src_repo.working_dir, dest_workdir=dest_workdir
        )
        await m.reflect(**kwargs)
        return m

    return _make_mirror
