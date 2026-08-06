"""Semantic reading of Fly-in map files.

Sits between :mod:`utils.parsing`, which only says whether a file is
well formed, and :mod:`utils.graph`, which needs objects rather than
lines. Every accepted line becomes a :class:`~utils.hub.Hub` or a
:class:`~utils.connection.Connection`, whose pydantic models give a
second layer of checks on the values themselves.
"""
from utils.parsing import Parsing
from utils.hub import Hub
from utils.connection import Connection


class Translator(Parsing):
    """Map file reader, turning valid lines into objects.

    Subclasses the validator so it can reuse its line readers, and
    assumes the file already passed
    :meth:`~utils.parsing.Parsing.parse_data`: nothing here reports a
    syntax error, a malformed line would simply break.

    Attributes:
        hubs: Zones read from the file, filled by :meth:`translate`.
        connections: Links read from the file, filled by the same.
        nb_drones: Fleet size declared by the map.
    """

    def __init__(self, path: str) -> None:
        """Prepare a reader for the map matched by ``path``.

        Args:
            path: Glob pattern; the first match is the file read.
        """
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.nb_drones: int = 0
        super().__init__(path)

    def _load_data_from_file(self) -> None:
        """Read the map file into ``data``, one entry per line.

        Raises:
            IndexError: If the pattern matches no file at all.
            OSError: If the file exists but cannot be read.
        """
        return super()._load_data_from_file()

    def _get_nb_drones(self) -> int:
        """Read the fleet size declared in the file.

        The whole file is walked instead of only its first line, so a
        later declaration wins over an earlier one.

        Returns:
            The number of drones to launch, 0 if no line declares it.
        """
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

    def _get_metadata_str(self, line: str) -> str:
        """Give the bracket block of a line, brackets stripped.

        Only the content is kept, the validity flag returned by the
        parent is dropped since the file is already validated.

        Args:
            line: Raw line from the map file.

        Returns:
            What sits between the brackets, empty when the line
            carries no block.
        """
        return super()._get_metadata_in_line(line)[1]

    def _fit_metadata(self, line: str) -> dict[str, str]:
        """Read a metadata block, filling in the missing keys.

        Which keys are expected depends on the line: a connection only
        takes a capacity, a zone takes a color, a zone type and a
        capacity. Any key left out of the block gets its default, so
        the caller always finds every key it needs.

        Args:
            line: Raw line from the map file, block included or not.

        Returns:
            Every key of the line kind, as strings still, the caller
            being the one converting the capacities to ints. Defaults
            are ``max_link_capacity`` at 1 for a connection, and
            ``color`` at grey, ``zone`` at normal and ``max_drones``
            at 1 for a zone.
        """
        line_s = line.strip().split(":")
        metadata_str = self._get_metadata_str(line)
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

    def _get_hub_name(self, line: str) -> str:
        """Give the zone name declared on a line.

        Args:
            line: Raw zone line from the map file.

        Returns:
            The name, first token after the colon.
        """
        return super()._get_name_in_line(line, 0)[2]

    def _get_coord(self, line: str) -> tuple[int, int]:
        """Give the coordinates declared on a zone line.

        Args:
            line: Raw zone line from the map file.

        Returns:
            The position of the zone on the map.
        """
        return super()._get_coord_in_line(line)[1]

    def _get_connection_in_line(self, line: str) -> set[str]:
        """Give the pair of zones a connection line links.

        Args:
            line: Raw connection line from the map file.

        Returns:
            The two ends as a set, so their order is not the one they
            were written in.
        """
        return super()._parse_data_connection(line)[1]

    def is_line_nb_drones(self, line: str) -> bool:
        """Tell whether a line declares the fleet size.

        Args:
            line: Raw line from the map file.

        Returns:
            True if the line opens with the ``nb_drones`` key, which
            makes :meth:`translate` skip it since the value was
            already read.
        """
        line_s = line.split(":")
        if line_s[0].strip() == "nb_drones":
            return True
        return False

    def translate(self) -> None:
        """Read the whole file into ``hubs`` and ``connections``.

        Blanks, comments and the fleet size line are skipped, the rest
        being sorted by key: a ``connection`` becomes a
        :class:`~utils.connection.Connection`, any other key a
        :class:`~utils.hub.Hub` keeping that key as its kind, which is
        how the graph later knows the start and end zones. Building
        those models is also where the values get checked, a capacity
        below 1 or a start zone declared restricted being refused
        here.

        Raises:
            IndexError: If the pattern matches no file at all.
            OSError: If the file exists but cannot be read.
            ValidationError: If a line holds a value the models
                refuse.
        """
        self._load_data_from_file()
        self.data = self.del_comment(self.data)
        self.nb_drones = self._get_nb_drones()
        for line in self.data:
            if self._skip_line(line):
                continue
            if self._ignore_hashtag(line):
                continue
            key = self._get_first_key(line)
            if self.is_line_nb_drones(line):
                continue
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
                    name=self._get_hub_name(line),
                    coord=self._get_coord(line),
                    color=hub_meta["color"],
                    max_drones=int(hub_meta["max_drones"]),
                    zone=hub_meta["zone"],
                    nb_drones_in=0,
                )
                self.hubs.append(hub)
