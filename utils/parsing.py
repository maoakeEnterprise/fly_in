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

    def _first_line(self, line: str, index: int) -> bool:
        line_strip = line.strip()
        tab_split = line_strip.split(":")
        number = int(tab_split[1])
        if tab_split[0] != "nb_drones":
            return False
        if number < 1:
            return False
        return True

    def _skip_line(self, line: str) -> bool:
        line_strip = line.strip()
        if line_strip == "":
            return True
        return False

    def parsing_data(self) -> None:
        self._load_data_from_file()
        index = 0
        index_com = 1
        for line in self.data:
            if self._skip_line(line):
                index += 1
                continue
            if (self._ignore_hashtag(line)):
                index_com += 1
                continue
            if index == 0:
                if not self._first_line(line, index):
                    raise ValueError("TEST")
        # do it something here
            index += 1
