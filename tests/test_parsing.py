from utils import Parsing


class TestParsing:

    def test_ignore_hashtag(self) -> None:
        line = "# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is True

    def test_ignore_hashtag_1(self) -> None:
        line = " \t\t\n# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is True

    def test_ignore_hashtag_2(self) -> None:
        line = " ca# qsdqdqsdqsd"
        parsing = Parsing("path")
        assert parsing._ignore_hashtag(line) is False

    def test_skip_line(self) -> None:
        line = "         "
        parsing = Parsing("titi")
        assert parsing._skip_line(line) is True

    def test_skip_line1(self) -> None:
        line = "      caca   "
        parsing = Parsing("titi")
        assert parsing._skip_line(line) is False

    def test_first_line(self) -> None:
        line = "nb_drones: 23"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 0) is True

    def test_first_line1(self) -> None:
        line = "nb_drones: 23"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 2) is False

    def test_first_line2(self) -> None:
        line = "nb_drones: zi"
        parsing = Parsing("titi")
        assert parsing._first_line(line, 0) is False
