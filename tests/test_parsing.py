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
