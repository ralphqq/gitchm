"""
Program entry point
"""
import asyncio
import logging
import os

from gitchm.init import (
    INIT,
    LOGLEVEL,
    REFLECT,
    ui,
)
from gitchm.mirror import CommitHistoryMirror
from gitchm.utils import format_stats


def main() -> None:
    try:
        logging.basicConfig(
            format='%(message)s',
            level=getattr(logging, LOGLEVEL)
        )
        logging.debug('Starting up')

        ui.start()
        init_params = ui.options[INIT]
        reflect_params = ui.options[REFLECT]

        chm = CommitHistoryMirror(**init_params)
        asyncio.run(chm.reflect(**reflect_params))
        logging.info(f'Done: {format_stats(chm.stats)}')
        if chm.stats['replicated'] > 0:
            logging.info(
                f'To view replicated commits, '
                f'go to directory {chm.dest_workdir}'
            )

    except KeyboardInterrupt:
        logging.info('Canceled')

    except Exception as e:
        logging.error(f'An unhandled error occurred: {e}')
