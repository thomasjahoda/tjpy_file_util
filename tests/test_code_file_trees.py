from pytest import fixture

import tjpy_file_util.code_file_trees as mut
from tjpy_file_util.code_file_trees import read_children_as_file_tree
from tjpy_file_util.temporary import create_temp_directory


@fixture
def base_dir():
    with create_temp_directory("tmp") as base_dir:
        yield base_dir


class TestCreateFileTreeAndReadChildrenAsFileTree:

    def test_single_file__dict_style__using_none(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, {
            "some_file.txt": None
        })
        assert base_dir.joinpath("some_file.txt").is_file()
        assert base_dir.joinpath("some_file.txt").read_text() == ""
        assert file_tree == read_children_as_file_tree(base_dir)

    def test_single_file__dict_style__using_item_type(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, {
            "some_file.txt": mut.FilesystemItemType.file
        })
        assert base_dir.joinpath("some_file.txt").is_file()
        assert base_dir.joinpath("some_file.txt").read_text() == ""
        assert file_tree == read_children_as_file_tree(base_dir)

    def test_single_file__list_style(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, [
            "some_file.txt"
        ])
        assert base_dir.joinpath("some_file.txt").is_file()
        assert base_dir.joinpath("some_file.txt").read_text() == ""
        assert file_tree == read_children_as_file_tree(base_dir)

    def test_single_file__list_style__tuple(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, [
            ("some_file.txt", mut.FilesystemItemType.file)
        ])
        assert base_dir.joinpath("some_file.txt").is_file()
        assert base_dir.joinpath("some_file.txt").read_text() == ""
        assert file_tree == read_children_as_file_tree(base_dir)

    def test_single_directory(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, {
            "sub_dir": mut.FilesystemItemType.directory
        })
        assert base_dir.joinpath("sub_dir").is_dir()
        assert file_tree == read_children_as_file_tree(base_dir)

    def test_sub_sub_dir_with_files(self, base_dir):
        file_tree = mut.create_file_tree(base_dir, {
            "sub_dir": {
                "sub_dir": ["some_file.txt", "some_file2.txt"]
            }
        })
        assert base_dir.joinpath("sub_dir").is_dir()
        assert base_dir.joinpath("sub_dir").joinpath("sub_dir").is_dir()
        assert base_dir.joinpath("sub_dir").joinpath("sub_dir").joinpath("some_file.txt").is_file()
        assert base_dir.joinpath("sub_dir").joinpath("sub_dir").joinpath("some_file2.txt").is_file()
        assert file_tree == read_children_as_file_tree(base_dir)
