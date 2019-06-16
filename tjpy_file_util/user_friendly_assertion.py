import logging
from pathlib import Path

_logger = logging.getLogger(__name__)


def assert_path_exists(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"The path {str(path)} does not exist")


def assert_path_is_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"The path {str(path)} does not exist but must be a file")
    if not path.is_file():
        raise FileNotFoundError(f"The path {str(path)} exists but must be a file")
