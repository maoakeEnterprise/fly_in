from utils.parsing import Parsing


class Translator(Parsing):
    def __init__(self, path: str) -> None:
        super().__init__(path)

    def _load_data_from_file(self) -> None:
        return super()._load_data_from_file()

    def _get_nb_drones(self) -> int:
        res: int = 0
        for line in self.data:
            if self._skip_line(line):
                continue
            if self._ignore_hashtag(line):
                continue
            line_s = line.strip()
            data = line_s.split(":")
            if data[0] == "nb_drones":
                res = int(data[1])
        return res

    def _get_metadata_in_line(self, line: str) -> str:
        return super()._get_metadata_in_line(line)[1]

    def _get_name_in_line(self, line) -> str:
        return super()._get_name_in_line(line, 0)[2]

    def _get_coord_in_line(self, line) -> tuple[int, int]:
        return super()._get_coord_in_line(line)[1]

    def _get_connection_in_line(self, line) -> set[str]:
        return super()._parse_data_connection(line)[1]

    def _get_first_key(self, line) -> str:
        return super()._get_first_key(line)
