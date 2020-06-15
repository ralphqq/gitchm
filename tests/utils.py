import os
import shutil


def create_dir(full_path: str, check_first: bool = False) -> None:
    """Creates directory if it does not yet exist."""
    if check_first:
            # Delete existing dir first
            delete_dir(full_path)

    if not os.path.exists(full_path):
        os.makedirs(full_path)


def delete_dir(full_path: str) -> None:
    """Deletes given path if it exists."""
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
