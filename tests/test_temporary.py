import tjpy_file_util.temporary as mut


def test_create_temp_file():
    with mut.create_temp_file("some_temporary_file") as tmp_file:
        assert tmp_file.is_file()
        assert "some_temporary_file" in tmp_file.name
    assert not tmp_file.is_file()


def test_create_temp_file__no_cleanup():
    with mut.create_temp_file("some_temporary_file", cleanup=False) as tmp_file:
        assert tmp_file.is_file()
        assert "some_temporary_file" in tmp_file.name
    assert tmp_file.exists()


def test_create_temp_file_for():
    with mut.create_temp_file("some_temporary_file") as some_file:
        file_content = "some text"
        some_file.write_text(file_content, encoding="utf-8")
        with mut.create_temp_file_for(some_file) as tmp_copy:
            assert str(some_file) != str(tmp_copy)
            assert tmp_copy.is_file()
            assert "some_temporary_file" in tmp_copy.name
            assert tmp_copy.read_text(encoding="utf-8") == file_content
        assert not tmp_copy.is_file()


def test_create_temp_file_for__custom_name():
    with mut.create_temp_file("some_temporary_file") as some_file:
        file_content = "some text"
        some_file.write_text(file_content, encoding="utf-8")
        with mut.create_temp_file_for(some_file, adapted_preferred_name="custom_name") as tmp_copy:
            assert str(some_file) != str(tmp_copy)
            assert tmp_copy.is_file()
            assert "custom_name" in tmp_copy.name
            assert tmp_copy.read_text(encoding="utf-8") == file_content
        assert not tmp_copy.is_file()


def test_create_temp_directory():
    with mut.create_temp_directory("some_temporary_directory") as tmp_directory:
        assert tmp_directory.is_dir()
        assert "some_temporary_directory" in tmp_directory.name
    assert not tmp_directory.is_dir()


def test_create_temp_directory__no_cleanup():
    with mut.create_temp_directory("some_temporary_directory", cleanup=False) as tmp_directory:
        assert tmp_directory.is_dir()
        assert "some_temporary_directory" in tmp_directory.name
    assert tmp_directory.is_dir()
