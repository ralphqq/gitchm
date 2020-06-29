"""
Fixtures used in mirror_init tests

Fixtures:
    modified_chm
"""
import pytest

from tests.utils import ModifiedCHM


@pytest.fixture
def modified_chm(init_source_repo):
    """Creates an instance of a ModifiedCHM object."""
    source_workdir, parent_dir_path, commit_data = init_source_repo
    mirror = ModifiedCHM(source_workdir)
    mirror._init_source_repo()
    return {
        'mirror': mirror,
        'source_workdir': source_workdir,
        'parent_dir': parent_dir_path,
        'commits': commit_data,
    }
