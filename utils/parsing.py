from glob import glob


class Parsing():
    def __init__(self, path: str) -> None:
        self.path = path
        self.data: list[str] = []

    def _load_data_from_file(self) -> None:
        data_str = ""
        path = self.path
        path_list = glob(path)
        path_extend = path_list[0]

        with open(path_extend, "r") as f:
            data_str = f.read()
            self.data = data_str.split("\n")

    def _print_data(self) -> None:
        self._load_data_from_file()
        for line in self.data:
            print(line)

    def _ignore_hashtag(self, line: str) -> bool:
        line_striped = line.strip()
        if line_striped.startswith("#"):
            return True
        return False

    def parsing_data(self) -> None:
        self._load_data_from_file()
