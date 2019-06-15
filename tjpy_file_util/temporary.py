import logging
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

_logger = logging.getLogger(__name__)


@contextmanager
def create_temp_file(preferred_name: str,
                     *,
                     cleanup: bool = True):
    temp_file: Optional[Path] = None
    try:
        temp_file = _create_temp_file(preferred_name)
        _logger.debug(f"created temp file {str(temp_file)}")
        yield temp_file
    finally:
        if cleanup and temp_file is not None and temp_file.is_file():
            _logger.debug(f"removing temp file {str(temp_file)}")
            temp_file.unlink()


@contextmanager
def create_temp_directory(preferred_name: str,
                          *,
                          cleanup: bool = True):
    temp_directory: Optional[Path] = None
    try:
        temp_directory = _create_temp_directory(preferred_name)
        _logger.debug(f"created temp directory {str(temp_directory)}")
        yield temp_directory
    finally:
        if cleanup and temp_directory is not None and temp_directory.is_dir():
            _logger.debug(f"removing temp directory {str(temp_directory)}")
            shutil.rmtree(temp_directory)


def _create_temp_directory(preferred_name: str) -> Path:
    system_temp_dir = Path(tempfile.gettempdir())
    temp_dir = system_temp_dir.joinpath(preferred_name)
    if temp_dir.exists():
        temp_dir = Path(tempfile.mkdtemp(prefix=preferred_name))
    else:
        temp_dir.mkdir(exist_ok=False)
    return temp_dir


def _create_temp_file(preferred_name: str) -> Path:
    system_temp_dir = Path(tempfile.gettempdir())
    temp_file = system_temp_dir.joinpath(preferred_name)
    if temp_file.exists():
        temporary_file_fd, temporary_file_name = tempfile.mkstemp(prefix=preferred_name)
        temp_file = Path(temporary_file_name)
    else:
        temp_file.touch(exist_ok=False)
    return temp_file


@contextmanager
def create_temp_file_for(file: Path,
                         *,
                         adapted_preferred_name: str = None,
                         cleanup: bool = True):
    assert file.is_file()
    preferred_name = adapted_preferred_name if adapted_preferred_name is not None else file.name
    with create_temp_file(preferred_name, cleanup=cleanup) as temp_file:
        temp_file.write_bytes(file.read_bytes())
        yield temp_file


@contextmanager
def create_temp_directory_for(directory: Path,
                              *,
                              adapted_preferred_name: str = None,
                              cleanup: bool = True):
    assert directory.is_dir()
    preferred_name = adapted_preferred_name if adapted_preferred_name is not None else directory.name
    with create_temp_directory(preferred_name, cleanup=cleanup) as temp_directory:
        temp_directory.rmdir()
        shutil.copytree(str(directory), str(temp_directory))
        yield temp_directory
