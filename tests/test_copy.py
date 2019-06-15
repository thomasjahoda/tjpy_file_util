from pathlib import Path

from pytest import fixture, fail

import tjpy_file_util.copy as mut
from tjpy_file_util.code_file_trees import create_file_tree, read_children_as_file_tree, unify
from tjpy_file_util.temporary import create_temp_directory


@fixture
def source_dir():
    with create_temp_directory("source_dir") as base_dir:
        yield base_dir


@fixture
def target_dir():
    with create_temp_directory("target_dir") as base_dir:
        yield base_dir


class TestCopyChildren:

    def test_no_children(self, source_dir: Path, target_dir: Path):
        mut.copy_children(source_dir, target_dir)
        assert len(list(target_dir.iterdir())) == 0

    def test_single_file_with_content(self, source_dir: Path, target_dir: Path):
        source_tree = create_file_tree(source_dir, {
            "file.txt": None
        })
        source_dir.joinpath("file.txt").write_text("content", encoding="utf-8")

        mut.copy_children(source_dir, target_dir)

        assert source_tree == read_children_as_file_tree(target_dir)
        assert target_dir.joinpath("file.txt").read_text(encoding="utf-8") == "content"

    def test_multiple_files(self, source_dir: Path, target_dir: Path):
        source_tree = create_file_tree(source_dir, {
            "file.txt": None,
            "file2.txt": None
        })

        mut.copy_children(source_dir, target_dir)

        assert read_children_as_file_tree(target_dir) == source_tree

    def test_conflicting_file(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "file.txt": None,
            "file2.txt": None
        })
        create_file_tree(target_dir, {
            "file2.txt": None
        })

        try:
            mut.copy_children(source_dir, target_dir)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "target file already exists" in ex.args[0]
            assert "file2.txt" in ex.args[0]

    def test_conflicting_directory(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "dir": [],
            "dir2": [],
        })
        create_file_tree(target_dir, {
            "dir2": [],
        })

        try:
            mut.copy_children(source_dir, target_dir,
                              merge_directories=False)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "target directory does already exist" in ex.args[0]
            assert "dir2" in ex.args[0]

    def test_conflicting_sub_file(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "dir": [],
            "dir2": ["file.txt"],
        })
        create_file_tree(target_dir, {
            "dir2": ["file.txt"],
        })

        try:
            mut.copy_children(source_dir, target_dir,
                              merge_directories=True)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "target file already exists" in ex.args[0]
            assert "dir2/file.txt" in ex.args[0]

    def test_merge_directories(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "dir": [],
            "dir2": ["file.txt"],
            "file3.txt": None,
        })
        create_file_tree(target_dir, {
            "dir2": ["file2.txt"],
        })

        mut.copy_children(source_dir, target_dir)

        assert read_children_as_file_tree(target_dir) == unify({
            "dir": [],
            "dir2": ["file.txt", "file2.txt"],
            "file3.txt": None,
        })

    def test_overwrite_files(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "file.txt": None,
        })
        source_dir.joinpath("file.txt").write_text("new_content")

        create_file_tree(target_dir, {
            "file.txt": None,
        })
        target_dir.joinpath("file.txt").write_text("old_content")

        mut.copy_children(source_dir, target_dir,
                          overwrite_files=True)

        assert target_dir.joinpath("file.txt").read_text() == "new_content"

    def test_conflict_of_file_to_dir(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "a": None,
        })

        create_file_tree(target_dir, {
            "a": [],
        })

        try:
            mut.copy_children(source_dir, target_dir,
                              overwrite_files=True,
                              merge_directories=True)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "because the target already exists and is no file" in ex.args[0]

    def test_conflict_of_dir_to_file(self, source_dir: Path, target_dir: Path):
        create_file_tree(source_dir, {
            "a": [],
        })

        create_file_tree(target_dir, {
            "a": None,
        })

        try:
            mut.copy_children(source_dir, target_dir,
                              overwrite_files=True,
                              merge_directories=True)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "because the target path already exists but is no directory" in ex.args[0]

    def test_source_dir_not_existing(self, source_dir: Path, target_dir: Path):
        try:
            fake_source_dir = source_dir.joinpath("not_existing")
            mut.copy_children(fake_source_dir, target_dir)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "source directory" in ex.args[0]
            assert "not_existing" in ex.args[0]

    def test_source_dir_is_file(self, source_dir: Path, target_dir: Path):
        try:
            fake_source_dir = source_dir.joinpath("is_file")
            fake_source_dir.touch()
            mut.copy_children(fake_source_dir, target_dir)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "source directory" in ex.args[0]
            assert "is_file" in ex.args[0]

    def test_target_dir_not_existing(self, source_dir: Path, target_dir: Path):
        try:
            fake_target_dir = source_dir.joinpath("not_existing")
            mut.copy_children(source_dir, fake_target_dir)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "target directory" in ex.args[0]
            assert "not_existing" in ex.args[0]

    def test_target_dir_is_file(self, source_dir: Path, target_dir: Path):
        try:
            fake_target_dir = target_dir.joinpath("is_file")
            fake_target_dir.touch()
            mut.copy_children(source_dir, fake_target_dir)
            fail("should have thrown exception")
        except mut.CopyException as ex:
            assert "target directory" in ex.args[0]
            assert "is_file" in ex.args[0]
