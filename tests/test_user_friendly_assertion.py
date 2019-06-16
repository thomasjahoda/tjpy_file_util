import tjpy_file_util.user_friendly_assertion as mut
from tjpy_file_util.temporary import create_temp_file


def test_assert_path_exists__success():
    with create_temp_file("some_file") as tmp_file:
        mut.assert_path_exists(tmp_file)


def assert_path_is_file__success():
    with create_temp_file("some_file") as tmp_file:
        mut.assert_path_is_file(tmp_file)
