import logging
from enum import unique, Enum
from pathlib import Path
from typing import Dict, Union, List, Tuple, cast, Any

_logger = logging.getLogger(__name__)


@unique
class DictFileHierarchyItemType(Enum):
    file = 1
    directory = 2


# recursive definition (original and correct one)
# DictFileHierarchy = Dict[str, Union['ListFileHierarchy', 'DictFileHierarchy', DictFileHierarchyItemType, None]]
# ListFileHierarchy = List[Union[str, Tuple[str, Union[DictFileHierarchy, DictFileHierarchyItemType]]]]
# FileHierarchy = Union[DictFileHierarchy, ListFileHierarchy]
# non-recursive definition because mypy does not support it yet (https://github.com/python/mypy/issues/731)
DictFileHierarchy = Dict[str, Union[List[Any], Dict[str, Any], DictFileHierarchyItemType, None]]
ListFileHierarchy = List[Union[str, Tuple[str, Union[DictFileHierarchy, DictFileHierarchyItemType]]]]
FileHierarchy = Union[DictFileHierarchy, ListFileHierarchy]


def create_file_tree(directory: Path, hierarchy: FileHierarchy):
    """
    Creates a file hierarchy in the specified directory.
    Examples for a file hierarchy:
    1. Dict style
    >>> {
    >>>     "example_file.txt": DictFileHierarchyItemType.file,
    >>>     "sub_dir": {"another_file.txt": DictFileHierarchyItemType.file},
    >>> }
    2. Dict style (but using None instead of DictFileHierarchyItemType.file)
    >>> {
    >>>     "example_file.txt": None,
    >>>     "sub_dir": {"another_file.txt": DictFileHierarchyItemType.file},
    >>> }
    3. Mixed dict and list style
    >>> {
    >>>     "example_file.txt": DictFileHierarchyItemType.file,
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
    if isinstance(hierarchy, list):
        dict_hierarchy = convert_to_dict_hierarchy(cast(ListFileHierarchy, hierarchy))
    else:
        dict_hierarchy = cast(DictFileHierarchy, hierarchy)
    _create_file_tree(directory, dict_hierarchy)


def _create_file_tree(directory: Path, dict_hierarchy: DictFileHierarchy):
    for key, value in dict_hierarchy.items():
        sub_item = directory.joinpath(key)
        if isinstance(value, list):
            value = convert_to_dict_hierarchy(cast(ListFileHierarchy, value))
        if isinstance(value, dict):
            sub_item.mkdir(exist_ok=False)
            _create_file_tree(sub_item, cast(DictFileHierarchy, value))
        if value is None:
            value = DictFileHierarchyItemType.file
        if isinstance(value, DictFileHierarchyItemType):
            if value == DictFileHierarchyItemType.file:
                sub_item.touch(exist_ok=False)
            elif value == DictFileHierarchyItemType.directory:
                sub_item.mkdir(exist_ok=False)


def convert_to_dict_hierarchy(list_hierarchy: ListFileHierarchy) -> DictFileHierarchy:
    dict_hierarchy: DictFileHierarchy = dict()
    for item in list_hierarchy:
        if isinstance(item, str):
            file_name = item
            if dict_hierarchy.get(file_name) is not None:
                raise Exception(f"duplicate items found with name {file_name}")
            dict_hierarchy[file_name] = DictFileHierarchyItemType.file
        elif isinstance(item, tuple):
            item_name = item[0]
            item_content: Union[DictFileHierarchy, DictFileHierarchyItemType] = item[1]
            if isinstance(item_content, dict):
                dict_hierarchy[item_name] = item_content
            elif isinstance(item_content, DictFileHierarchyItemType):
                dict_hierarchy[item_name] = item_content
            else:
                raise Exception(f"unknown item content {item_content}")
    return dict_hierarchy
