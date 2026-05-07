from __future__ import annotations

import os
import sys

from loguru import logger


def setup_logging() -> None:
    logger.remove()

    level = os.environ.get("LOGGING_LEVEL", "INFO").upper()

    stderr_fmt = "{time:HH:mm:ss} | {level:<8} | {message}"
    logger.add(sys.stderr, level=level, format=stderr_fmt)

    file_fmt = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8}"
        " | {name}:{function}:{line} | {message}"
    )
    logger.add(
        "logs/cc_monitor.log",
        level="DEBUG",
        format=file_fmt,
        rotation="10 MB",
        serialize=True,
    )
