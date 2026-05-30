import pytest
from utils import FlagManager


class TestFlagManager:

    def test_load_args(self) -> None:
        parsing = FlagManager()
        parsing.init_args([])
        assert len(parsing._get_args_values()) == 11

    def test_flag_error_with_two_flag(self) -> None:
        with pytest.raises(ValueError):
            parsing = FlagManager()
            parsing.init_args(["--launch_H3", "--launch_H2"])
            v = parsing._get_args_values()
            parsing._flag_check(v)

    def test_flag_error_with_no_flag(self) -> None:
        with pytest.raises(ValueError):
            parsing = FlagManager()
            parsing.init_args([])
            v = parsing._get_args_values()
            parsing._flag_check(v)

    def test_flag_value(self) -> None:
        parsing = FlagManager()
        parsing.init_args(["--launch_H3"])
        v = parsing.get_path_from_flag()
        assert v == "maps/hard/03*"

    def test_flag_graphed(self) -> None:
        parsing = FlagManager()
        parsing.init_args(["--launch_H3", "--graph"])
        assert parsing.is_graphed() is True

    def test_flag_graphed_not_present(self) -> None:
        parsing = FlagManager()
        parsing.init_args(["--launch_H3"])
        assert parsing.is_graphed() is False
