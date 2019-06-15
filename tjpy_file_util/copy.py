import logging
import shutil
from pathlib import Path

_logger = logging.getLogger(__name__)


class CopyException(Exception):
    pass


def copy_children(source_dir: Path,
                  target_dir: Path,
                  *,
                  merge_directories: bool = True,
                  overwrite_files: bool = False):
    """Low performance function for copying tree of files but providing some additional options"""
    if not source_dir.exists():
        raise CopyException(f"The source directory '{source_dir}' must exist.")
    if not source_dir.is_dir():
        raise CopyException(f"The provided source directory path '{source_dir}' exists but is no directory.")
    if not target_dir.exists():
        raise CopyException(f"The target directory '{target_dir}' must exist.")
    if not target_dir.is_dir():
        raise CopyException(f"The provided target directory path '{target_dir}' exists but is no directory.")
    for source_child in source_dir.iterdir():
        target_path_for_child = target_dir.joinpath(source_child.name)
        copy(source_child, target_path_for_child,
             merge_directories=merge_directories, overwrite_files=overwrite_files)


def copy(source: Path,
         target: Path,
         *,
         merge_directories: bool = True,
         overwrite_files: bool = False):
    """
    Copy source file or directory to target path.
    Use shutil.copytree or rsync for higher performance.
    :param source:
    :param target:
    :param merge_directories:
    :param overwrite_files:
    :return:
    """
    if source.is_dir():
        if target.exists() and not target.is_dir():
            raise CopyException(
                f"The source directory '{source}' can not be copied to '{target}' "
                f"because the target path already exists but is no directory.")
        if not merge_directories and target.exists():

            raise CopyException(f"The source directory '{source}' can not be copied to '{target}' "
                                f"because the target directory does already exist and merging directories is disabled")
        _logger.debug(f"Copying directory {source} to {target}")
        target.mkdir(exist_ok=merge_directories)
        copy_children(source, target,
                      merge_directories=merge_directories,
                      overwrite_files=overwrite_files)
        # shutil.copytree(child, target_path_for_child, ) # not used because not configurable enough
    else:
        if target.exists():
            if target.exists() and not target.is_file():
                raise CopyException(f"The file '{source}' can not be copied to '{target}' "
                                    f"because the target already exists and is no file.")
            if not overwrite_files:
                raise CopyException(f"The file '{source}' can not be copied to '{target}' "
                                    f"because the target file already exists and overwriting files is disabled.")
            else:
                _logger.debug(f"Deleting {target} to overwrite it with {source}")
                target.unlink()
        _logger.debug(f"Copying file {source} to {target}")
        shutil.copyfile(str(source), str(target))
