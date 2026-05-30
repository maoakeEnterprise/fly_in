import pytest
from utils import Parsing


class TestParsing:

    def test_load_args(self) -> None:
        parsing = Parsing()
        parsing.init_args()
        assert len(parsing.get_args_values()) == 10

    def test_error_load(self) -> None:
        with pytest.raises(FileNotFoundError):
            with open("cc", "r") as f:
                f.buffer()
