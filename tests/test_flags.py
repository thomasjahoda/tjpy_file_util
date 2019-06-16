import tjpy_file_util.flags as mut
from tjpy_file_util.temporary import create_temp_file


def test_make_file_executable_if_necessary():
    with create_temp_file("some_file") as tmp_file:
        assert not mut.is_executable(tmp_file)
        mut.make_file_executable_if_necessary(tmp_file)
        assert mut.is_executable(tmp_file)
        mut.make_file_executable_if_necessary(tmp_file)
        assert mut.is_executable(tmp_file)
