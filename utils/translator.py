from utils.parsing import Parsing
from utils.hub import Hub
from utils.connection import Connection


class Translator(Parsing):
    def __init__(self, path: str) -> None:
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.nb_drones: int = 0
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

    def _fit_metadata(self, line: str) -> dict[str, str]:
        line_s = line.strip().split(":")
        metadata_str = self._get_metadata_in_line(line)
        if line_s[0] == "connection":
            metadata = {
                "max_link_capacity": "1"
            }
            metadata_split = metadata_str.split(" ")
            for data in metadata_split:
                sub_data = data.split("=")
                if sub_data[0].strip() == "max_link_capacity":
                    metadata["max_link_capacity"] = sub_data[1]
        else:
            metadata = {
                "color": "grey",
                "zone": "normal",
                "max_drones": "1"
            }
            metadata_split = metadata_str.split(" ")
            for data in metadata_split:
                sub_data = data.split("=")
                if sub_data[0].strip() == "color":
                    metadata["color"] = sub_data[1]
                elif sub_data[0].strip() == "zone":
                    metadata["zone"] = sub_data[1]
                elif sub_data[0].strip() == "max_drones":
                    metadata["max_drones"] = sub_data[1]
        return metadata

    def _get_name_in_line(self, line) -> str:
        return super()._get_name_in_line(line, 0)[2]

    def _get_coord_in_line(self, line) -> tuple[int, int]:
        return super()._get_coord_in_line(line)[1]

    def _get_connection_in_line(self, line) -> set[str]:
        return super()._parse_data_connection(line)[1]

    def _get_first_key(self, line) -> str:
        return super()._get_first_key(line)

    def translate(self) -> None:
        self._load_data_from_file()
        self.nb_drones = self._get_nb_drones()
        for line in self.data:
            if self._skip_line(line):
                continue
            if self._ignore_hashtag(line):
                continue
            key = self._get_first_key(line)
            if key == "connection":
                conn_names = list(self._get_connection_in_line(line))
                conn_meta = self._fit_metadata(line)
                connection = Connection(
                    name_hub1=conn_names[0],
                    name_hub2=conn_names[1],
                    max_link=int(conn_meta["max_link_capacity"]),
                    nb_drones_in=0
                )
                self.connections.append(connection)
            else:
                hub_meta = self._fit_metadata(line)
                hub = Hub(
                    type_hub=self._get_first_key(line),
                    name=self._get_name_in_line(line),
                    coord=self._get_coord_in_line(line),
                    color=hub_meta["color"],
                    max_drones=int(hub_meta["max_drones"]),
                    zone=hub_meta["zone"],
                    nb_drones_in=0,
                )
                self.hubs.append(hub)
