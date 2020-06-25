import asyncio
from unittest.mock import AsyncMock

import pytest

from app.mirror import CommitHistoryMirror

SIDE_EFFECT = [
    'replicated',
    'skipped',
    'replicated',
    'failed',
    'skipped',
    'failed',
]


class TestReplicate:

    @pytest.fixture
    def mirror(self, chm, mocker):
        mocker.patch.object(
            target=CommitHistoryMirror,
            attribute='_commit',
            new_callable=AsyncMock
        )
        return chm['mirror']

    @pytest.mark.asyncio
    async def test_replicate_with_commits(self, mirror, iter_commits):
        mirror._commit.side_effect= SIDE_EFFECT
        await mirror._replicate(iter_commits)

        assert mirror._commit.call_count == len(SIDE_EFFECT)
        assert mirror.stats['replicated'] == SIDE_EFFECT.count('replicated')
        assert mirror.stats['skipped'] == SIDE_EFFECT.count('skipped')
        assert mirror.stats['failed'] == SIDE_EFFECT.count('failed')

    @pytest.mark.asyncio
    async def test_replicate_with_no_commits(
            self,
            mirror,
            empty_iter_commits,
            mocker
        ):
        mocker.patch.object(asyncio, 'as_completed', new_callable=AsyncMock)
        await mirror._replicate(empty_iter_commits)

        assert not mirror._commit.called
        assert not asyncio.as_completed.called
        assert mirror.stats['replicated'] == 0
        assert mirror.stats['skipped'] == 0
        assert mirror.stats['failed'] == 0
