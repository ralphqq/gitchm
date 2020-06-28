"""
End-to-end test for mirror ops with various options/params 
passed to `reflect()`

Classes:
"""
import operator

import pytest

from app.utils import delete_dir
from tests.utils import (
    DEST_FEATURE_COMMITS,
    DEST_MASTER_COMMITS,
    FEATURE_BRANCH,
    listify_attribute,
    load_iter_commits,
    read_gitchm
)

NOBODY = 'nobody'   # name of unknown author/committer
PARAMS = {
    '1st': {'author': 'jimmy page'},
    '2nd': {'committer': 'robert.plant@gmail.com'},
    '3rd': {'author': 'jimmy.page@gmail.com', 'committer': 'John Bonham'},
    '4th': {'before': 1591798441},
    '5th': {'after': 1591798441},
    '6th': {'after': 1588719285, 'before': 1591798441},
    '7th': {'author': NOBODY},
}


class TestMirrorOpsReflectOptions:
    """Mirror ops on destination repo's master branch."""

    @pytest.fixture(params=PARAMS.values(), ids=PARAMS.keys())
    async def init_cases(self, request, init_mirror, dest_repo_tree):
        options = request.param
        mirror = await init_mirror(
            dest_workdir=dest_repo_tree.working_dir,
            **options
        )
        yield mirror, options
        delete_dir(mirror.dest_repo.working_dir)

    @pytest.mark.asyncio
    async def test_something(self, init_cases):
        m, options = init_cases
        eq_ne = operator.ne
        expected_replicated = 0

        if options.get('author') == NOBODY:
            # Special case, use equality to assert x == 0
            eq_ne = operator.eq

        else:
            # Assertion specific only to scenarios where
            # there are matched commits

            # Get list of commit hashes from source and .gitchmirror
            src_commits = load_iter_commits(
                repo=m.source_repo,
                branch='master',
                mode='obj',
                **options
            )
            src_hashes = listify_attribute(src_commits, 'hexsha')
            dst_replicated_hashes = read_gitchm(m.dest_repo.working_dir)
            expected_replicated = len(src_commits)
            print(f'x-x: {expected_replicated}')
            print(f'y-y: {len(dst_replicated_hashes)}')

            assert set(src_hashes) == set(dst_replicated_hashes)

        # Assertions to be made on all scenarios
        assert eq_ne(m.stats['replicated'], 0)  # 0 or non-zero
        assert m.stats['replicated'] == expected_replicated
        assert m.stats['failed'] == 0
        assert m.stats['skipped'] == 0
