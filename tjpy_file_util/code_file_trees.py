import logging
from enum import unique, Enum
from pathlib import Path
from typing import Dict, Union, List, Tuple, cast, Any

_logger = logging.getLogger(__name__)


@unique
class FilesystemItemType(Enum):
    file = 1
    directory = 2


# recursive definition (original and correct one)
# DictFileHierarchy = Dict[str, Union['ListFileHierarchy', 'DictFileHierarchy', DictFileHierarchyItemType, None]]
# ListFileHierarchy = List[Union[str, Tuple[str, Union[DictFileHierarchy, DictFileHierarchyItemType]]]]
# _StrictDictFileHierarchyItemValue = Union[Dict[str, 'DictFileHierarchy'], DictFileHierarchyItemType]
# StrictDictFileHierarchy = Dict[str, _StrictDictFileHierarchyItemValue]
# FileHierarchy = Union[DictFileHierarchy, ListFileHierarchy]  # unable to add StrictDictFileHierarchy cos of mypy bug

# non-recursive definition because mypy does not support it yet (https://github.com/python/mypy/issues/731)
DictFileHierarchy = Dict[str, Union[List[Any], Dict[str, Any], FilesystemItemType, None]]
ListFileHierarchy = List[Union[str, Tuple[str, Union[DictFileHierarchy, FilesystemItemType]]]]
_StrictDictFileHierarchyItemValue = Union[Dict[str, Any], FilesystemItemType]
StrictDictFileHierarchy = Dict[str, _StrictDictFileHierarchyItemValue]
FileHierarchy = Union[DictFileHierarchy, ListFileHierarchy]  # unable to add StrictDictFileHierarchy cos of mypy bug


def create_file_tree(directory: Path, hierarchy: FileHierarchy) -> StrictDictFileHierarchy:
    """
    Creates a file hierarchy in the specified directory.
    Examples for a file hierarchy:
    1. Dict style
    >>> {
    >>>     "example_file.txt": FilesystemItemType.file,
    >>>     "sub_dir": {"another_file.txt": FilesystemItemType.file},
    >>> }
    2. Dict style (but using None instead of DictFileHierarchyItemType.file)
    >>> {
    >>>     "example_file.txt": None,
    >>>     "sub_dir": {"another_file.txt": FilesystemItemType.file},
    >>> }
    3. Mixed dict and list style
    >>> {
    >>>     "example_file.txt": FilesystemItemType.file,
    >>>     "sub_dir": ["another_file.txt"],
    >>> }
    4. List style only
    >>> [
    >>>     "example_file.txt",
    >>>     ("sub_dir", ["another_file.txt"])
    >>> ]
    :param directory: directory where all files will be created at
    :param hierarchy: directories and files
    :return:
    """
    assert directory.is_dir()
    dict_hierarchy = unify(hierarchy)
    _create_file_tree(directory, dict_hierarchy)
    return dict_hierarchy


def _create_file_tree(directory: Path, dict_hierarchy: StrictDictFileHierarchy):
    for key, value in dict_hierarchy.items():
        sub_item = directory.joinpath(key)
        if isinstance(value, dict):
            sub_item.mkdir(exist_ok=False)
            _create_file_tree(sub_item, cast(StrictDictFileHierarchy, value))
        elif isinstance(value, FilesystemItemType):
            if value == FilesystemItemType.file:
                sub_item.touch(exist_ok=False)
            elif value == FilesystemItemType.directory:
                sub_item.mkdir(exist_ok=False)
        else:
            raise Exception(f"invalid value for item with key '{key}': '{value}'")


def unify(hierarchy: FileHierarchy) -> StrictDictFileHierarchy:
    if isinstance(hierarchy, list):
        return _convert_to_strict_dict_hierarchy(cast(ListFileHierarchy, hierarchy))
    else:
        dict_hierarchy = cast(DictFileHierarchy, hierarchy)
        corrected_dict_hierarchy: StrictDictFileHierarchy = dict()
        for key, value in dict_hierarchy.items():
            corrected_value: _StrictDictFileHierarchyItemValue
            if isinstance(value, list):
                corrected_value = _convert_to_strict_dict_hierarchy(cast(ListFileHierarchy, value))
            elif isinstance(value, dict):
                corrected_value = unify(cast(DictFileHierarchy, value))
            elif value is None:
                corrected_value = FilesystemItemType.file
            elif isinstance(value, FilesystemItemType):
                if value == FilesystemItemType.file:
                    corrected_value = FilesystemItemType.file
                elif value == FilesystemItemType.directory:
                    corrected_value = dict()
                else:
                    raise Exception(f"invalid value for item with key '{key}': '{value}'")
            else:
                raise Exception(f"invalid value for item with key '{key}': '{value}'")
            corrected_dict_hierarchy[key] = corrected_value
        return corrected_dict_hierarchy


def _convert_to_strict_dict_hierarchy(list_hierarchy: ListFileHierarchy) -> StrictDictFileHierarchy:
    dict_hierarchy: StrictDictFileHierarchy = dict()
    for item in list_hierarchy:
        if isinstance(item, str):
            file_name = item
            if dict_hierarchy.get(file_name) is not None:
                raise Exception(f"duplicate items found with name {file_name}")
            dict_hierarchy[file_name] = FilesystemItemType.file
        elif isinstance(item, tuple):
            item_name = item[0]
            item_content: Union[DictFileHierarchy, FilesystemItemType] = item[1]
            if isinstance(item_content, dict):
                dict_hierarchy[item_name] = unify(cast(DictFileHierarchy, item_content))
            elif isinstance(item_content, FilesystemItemType):
                dict_hierarchy[item_name] = item_content
            else:
                raise Exception(f"unknown item content {item_content}")
    return dict_hierarchy


def read_children_as_file_tree(directory: Path) -> StrictDictFileHierarchy:
    assert directory.is_dir()
    dict_hierarchy: StrictDictFileHierarchy = dict()
    for item in directory.iterdir():
        if item.is_file():
            dict_hierarchy[item.name] = FilesystemItemType.file
        elif item.is_dir():
            dict_hierarchy[item.name] = read_children_as_file_tree(item)
        else:
            _logger.debug(f"{read_children_as_file_tree.__name__}: Ignoring {item} because it is "
                          f"neither a file nor a directory")
    return dict_hierarchy
