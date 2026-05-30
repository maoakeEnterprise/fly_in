import pytest
from utils import Parsing


class TestParsing:

    def test_load_args(self) -> None:
        parsing = Parsing()
        parsing.init_args([])
        assert len(parsing._get_args_values()) == 10

    def test_flag_error(self) -> None:
        with pytest.raises(ValueError):
            parsing = Parsing()
            parsing.init_args(["--launch_H3", "--launch_H2"])
            parsing._is_one_flag()
