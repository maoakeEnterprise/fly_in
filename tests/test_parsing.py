import pytest
from utils import Parsing


class TestParsing:

    def test_load_args(self) -> None:
        parsing = Parsing()
        parsing.init_args([])
        assert len(parsing._get_args_values()) == 10

    def test_flag_error_with_two_flag(self) -> None:
        with pytest.raises(ValueError):
            parsing = Parsing()
            parsing.init_args(["--launch_H3", "--launch_H2"])
            v = parsing._get_args_values()
            parsing._is_one_flag(v)

    def test_flag_error_with_no_flag(self) -> None:
        with pytest.raises(ValueError):
            parsing = Parsing()
            parsing.init_args([])
            v = parsing._get_args_values()
            parsing._is_one_flag(v)

    def test_flag_value(self) -> None:
        parsing = Parsing()
        parsing.init_args(["--launch_H3"])
        v = parsing.get_flag_value()
        assert v == "maps/hard/03*"
