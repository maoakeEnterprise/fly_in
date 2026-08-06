"""Syntactic validation of Fly-in map files.

Checks a map against the format described in the subject, in two
passes: whole-file rules first, such as the presence of a unique start
and end zone, then line-by-line rules on metadata and connections.
Problems are collected rather than raised, so a single run reports
them all with their line number.
"""
from glob import glob
from enum import Enum
import re


class HubName(Enum):
    """Line keys that declare a zone."""

    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"


class KeyName(Enum):
    """Every line key a map file may open with."""

    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    CONNECTION = "connection"
    NB_DRONES = "nb_drones"


class NameMetaData(Enum):
    """Metadata keys allowed inside a zone declaration."""

    ZONE = "zone"
    COLOR = "color"
    MAX_D = "max_drones"


class NameMetaDataC(Enum):
    """Metadata keys allowed inside a connection declaration."""

    MAX_LINK = "max_link_capacity"


class KeyNameZone(Enum):
    """Accepted values of the ``zone`` metadata key."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Parsing():
    """Syntax validator for a single map file.

    Only tells whether a file can be read, never what it means:
    turning valid lines into zones and connections is the job of the
    translator, which subclasses this one.

    Attributes:
        path: Glob pattern of the map to read.
        data: Lines of the file, blanks and comments included, filled
            by :meth:`_load_data_from_file`.
    """

    def __init__(self, path: str) -> None:
        """Prepare a validator for the map matched by ``path``.

        Args:
            path: Glob pattern; the first match is the file read.
        """
        self.path = path
        self.data: list[str] = []

    def _load_data_from_file(self) -> None:
        """Read the map file into ``data``, one entry per line.

        The path is expanded as a glob and only the first match is
        kept, which is what lets a flag name a map by prefix.

        Raises:
            IndexError: If the pattern matches no file at all.
            OSError: If the file exists but cannot be read.
        """
        data_str = ""
        path = self.path
        path_list = glob(path)
        path_extend = path_list[0]

        with open(path_extend, "r") as f:
            data_str = f.read()
            self.data = data_str.split("\n")

    def _print_data(self) -> None:
        """Reload the file and print every line, for debugging."""
        self._load_data_from_file()
        for line in self.data:
            print(line)

    def _ignore_hashtag(self, line: str) -> bool:
        """Tell whether a line is a comment.

        Only a whole-line comment counts. A ``#`` sitting after a
        declaration does not open a comment, so it stays part of the
        line and makes the later checks fail.

        Args:
            line: Raw line from the map file.

        Returns:
            True if the line starts with ``#`` once stripped.
        """
        line_striped = line.strip()
        if line_striped.startswith("#"):
            return True
        return False

    def _first_line(self, line: str, index: int) -> bool:
        """Check the fleet size declaration opening the file.

        Args:
            line: Raw line to check.
            index: Rank of the line among the meaningful ones; only
                rank 0 may carry the declaration.

        Returns:
            True if the line reads ``nb_drones: <n>`` with ``n`` a
            strictly positive integer.
        """
        if index != 0:
            return False
        line_strip = line.strip()
        tab_split = line_strip.split(":")
        if len(tab_split) != 2:
            return False
        line_number = tab_split[1].strip()
        if not line_number.isdigit():
            return False
        number = int(tab_split[1])
        if tab_split[0] != "nb_drones":
            return False
        if number < 1:
            return False
        return True

    def _skip_line(self, line: str) -> bool:
        """Tell whether a line is blank.

        Args:
            line: Raw line from the map file.

        Returns:
            True if nothing is left once the line is stripped.
        """
        line_strip = line.strip()
        if line_strip == "":
            return True
        return False

    def _unique_hub(self, data: list[str], name_hub: str
                    ) -> tuple[bool, int, str]:
        """Check that a zone keyword is declared at most once.

        The keyword is also rejected when it hides inside a longer
        key, so a typo such as ``my_start_hub`` is caught here.

        Args:
            data: Lines of the map file.
            name_hub: Keyword to count, ``"start_hub"`` for instance.

        Returns:
            A ``(ok, line, message)`` triplet: ``ok`` is False on
            error, ``line`` is the 1-based line reached, and
            ``message`` describes the problem, empty on success.
        """
        len_nh = 0
        index = 1
        for line in data:
            if self._skip_line(line) or self._ignore_hashtag(line):
                index += 1
                continue
            tab_l = line.split(":")
            new_l = tab_l[0].strip()

            if not new_l.startswith(name_hub) and name_hub in new_l:
                return (False, index, "This hub is no unique")
            len_nh += line.count(name_hub)
            if len_nh > 1:
                return (False, index,  "This hub is no unique")
            index += 1
        return (True, index, "")

    def _start_end_present(self, data: list[str]) -> tuple[bool, int, str]:
        """Check that both a start and an end zone are declared.

        Args:
            data: Lines of the map file.

        Returns:
            A ``(ok, line, message)`` triplet, ``line`` being -1 on
            error since the failure belongs to no single line.
        """
        start = False
        end = False
        for line in data:
            tab_l = line.split(":")
            if tab_l[0].strip() == HubName.START_HUB.value:
                start = True
            if tab_l[0].strip() == HubName.END_HUB.value:
                end = True
        if start is False or end is False:
            return (False, -1, "Must have one start_hub or end_hub")
        return (True, 0, "")

    def _is_len_split_two_point(self, data: list[str]
                                ) -> tuple[bool, int, str]:
        """Check that every line carries exactly one colon.

        Blank and comment lines are skipped.

        Args:
            data: Lines of the map file.

        Returns:
            A ``(ok, line, message)`` triplet pointing at the first
            line holding no colon or several of them.
        """
        index = 1
        for line in data:
            if self._skip_line(line):
                index += 1
                continue
            if self._ignore_hashtag(line):
                index += 1
                continue
            tab_l = line.split(":")
            if len(tab_l) != 2:
                return (False, index, "Too much data in this "
                                      "line format > data1 : data2")
            index += 1
        return (True, index, "")

    def _get_main_keys(self, data: list[str]) -> list[str]:
        """Collect what stands before the colon on every line.

        Args:
            data: Lines of the map file.

        Returns:
            One entry per input line, blanks and comments included,
            so the result stays aligned on ``data``.
        """
        keys = [line.strip().split(":")[0] for line in data]
        return keys

    def _unique_name_hub(self, data: list[str]) -> tuple[bool, int, str]:
        """Check that no two zones share a name.

        Connection lines are skipped, blanks and comments too. A name
        is also rejected when it holds anything but word characters,
        which is what forbids dashes and spaces.

        Args:
            data: Lines of the map file.

        Returns:
            A ``(ok, line, message)`` triplet pointing at the first
            malformed or repeated name.
        """
        names: set[str] = set()
        index = 1
        for line in data:
            if self._ignore_hashtag(line):
                index += 1
                continue
            if self._skip_line(line):
                index += 1
                continue
            if self._get_first_key(line) == "connection":
                index += 1
                continue
            res = self._get_name_in_line(line, index)
            name = res[2]
            if res[0] is False or name in names:
                return (False, index, "format name hub is not good or unique"
                                      "name hub")
            names.add(name)
            index += 1
        return (True, index, "")

    def _get_first_key(self, line: str) -> str:
        """Give what stands before the first colon of a line.

        Args:
            line: Raw line from the map file.

        Returns:
            The stripped key, or the whole line when it carries no
            colon.
        """
        line_s = line.split(":")
        return line_s[0].strip()

    def _get_name_in_line(self, line: str, index: int
                          ) -> tuple[bool, int, str]:
        """Read the zone name declared on a line.

        Only the first token after the colon is looked at, and it has
        to be made of word characters alone.

        Args:
            line: Raw line from the map file.
            index: Line number, passed through untouched so callers
                can report it.

        Returns:
            A ``(ok, index, name)`` triplet. On failure ``name``
            holds the offending token instead, empty when the line
            carries no usable colon.
        """
        line_s = line.split(":")
        regex = r"^(\w+)$"
        name: str = ""
        if len(line_s) != 2:
            return (False, index, name)
        new_line = line_s[1].strip()
        data = new_line.split(" ")
        for word in data:
            res = re.search(regex, word)
            if res is None:
                return (False, index, word)
            name = word
            break
        return (True, index, name)

    def _get_coord_in_line(self, line: str) -> tuple[bool, tuple[int, int]]:
        """Read the coordinates declared on a zone line.

        Every token after the colon reading as a signed integer is
        collected, and there must be exactly two of them.

        Args:
            line: Raw line from the map file.

        Returns:
            A ``(ok, coord)`` pair, ``coord`` falling back to
            ``(0, 0)`` when the line holds no usable pair.
        """
        regex = r"^[+-]?\d+$"
        list_int: list[str] = []
        line_s = line.split(":")
        if len(line_s) != 2:
            return (False, (0, 0))
        new_l = line_s[1].strip()
        data = new_l.split(" ")
        for data_s in data:
            res = re.search(regex, data_s)
            if res:
                list_int.append(data_s)
        if len(list_int) != 2:
            return (False, (0, 0))
        return (True, (int(list_int[0]), int(list_int[1])))

    def del_comment(self, data: list[str]) -> list[str]:
        new_data: list[str] = []
        for line in data:
            new_data.append(line.split("#")[0])
        return new_data

    def _get_metadata_in_line(self, line: str) -> tuple[bool, str]:
        """Extract the bracket block closing a line.

        The block is only accepted at the very end of the line, so
        anything trailing after the closing bracket is an error. The
        keys themselves are left to :meth:`_parse_metadata`.

        Args:
            line: Raw line from the map file.

        Returns:
            A ``(ok, metadata)`` pair, ``metadata`` holding what sits
            between the brackets, empty when the line carries none.
            On failure it holds the misplaced block instead.
        """
        metadata_str: str = ""
        line = line.strip()
        match = re.search(r"\s+\[(.*?)\]", line)
        match_with = re.search(r"\s+(\[.*?\])", line)
        if match_with:
            test_metadata_str = match_with.group(1)
            if not line.endswith(test_metadata_str):
                return (False, test_metadata_str)
        if match:
            metadata_str = match.group(1)
            metadata_str.strip()
        return (True, metadata_str)

    def _parse_metadata(self, metadata: str, keys: set[str]) -> bool:
        """Check the keys and values of a metadata block.

        Every entry must read ``key=value`` with a key taken from
        ``keys``, and no key may appear twice since each one is
        consumed as it is met. A ``zone`` value has to name a known
        zone type, and a capacity has to be a strictly positive
        integer.

        Args:
            metadata: Block content, brackets already stripped.
            keys: Keys allowed here, which differ between a zone and
                a connection.

        Returns:
            True if every entry is well formed.
        """
        data = metadata.strip().split(" ")
        keys_c = keys.copy()
        for tmp in data:
            k_v = tmp.split("=")
            if len(k_v) != 2:
                return False
            if k_v[0] in keys_c:
                if k_v[0].strip() == "zone":
                    if k_v[1].strip() not in KeyNameZone:
                        return False
                if (k_v[0].strip() == "max_drones"
                   or k_v[0].strip() == "max_link_capacity"):
                    if k_v[1].isdigit() is False:
                        return False
                    c = int(k_v[1])
                    if c < 1:
                        return False
                keys_c.remove(k_v[0])
            else:
                return False
        return True

    def _there_is_metadata(self, line: str) -> bool:
        """Tell whether a line seems to carry a metadata block.

        Decided by counting the tokens after the colon: a zone needs
        a name and two coordinates, a connection only a pair of
        names, so anything beyond that must be a block.

        Args:
            line: Raw line from the map file.

        Returns:
            True if a block seems present, without checking it.
        """
        line_s = line.split(":")
        name = line_s[0]
        index_md = 2 if name == "connection" else 3
        add_md = 0 if name == "connection" else 1
        data = line_s[1].strip().split(" ")
        if len(data) < index_md + add_md:
            return False
        return True

    def _parse_data_connection(self, line: str) -> tuple[bool, set[str]]:
        """Read the pair of zones a connection line links.

        Args:
            line: Raw connection line from the map file.

        Returns:
            A ``(ok, names)`` pair. ``names`` is a set, so the two
            ends are unordered and a zone linked to itself collapses
            to a single entry, which the later checks reject.
        """
        conn_set: set[str] = set()
        data = line.strip().split(":")[1].strip().split(" ")
        connection = data[0].split("-")
        if len(connection) != 2:
            return (False, conn_set)
        conn_set.add(connection[0])
        conn_set.add(connection[1])
        return (True, conn_set)

    def _get_names_hub(self) -> set[str]:
        """Collect every token standing in zone name position.

        No line is filtered out, so connection lines and blanks throw
        in their own token too. The result is only meant to be
        intersected with a connection pair, where those leftovers
        cannot match.

        Returns:
            Zone names read across the file, plus the leftovers of
            the lines declaring no zone.
        """
        names = set()
        for line in self.data:
            names.add(self._get_name_in_line(line, 0)[2])
        return names

    def _connection_names_exist(self, names: set[str], connection: set[str]
                                ) -> bool:
        """Check that both ends of a connection name known zones.

        Args:
            names: Zone names declared in the file.
            connection: Pair of names read on the connection line.

        Returns:
            True when both ends are known, which also rules out a
            zone linked to itself since such a pair holds one name.
        """
        verif_set = names.intersection(connection)
        if len(verif_set) != 2:
            return False
        return True

    def _uniq_connection(self, connections: list[set[str]],
                         connection: set[str]) -> bool:
        """Check that a connection was not already declared.

        Ends being held in sets, ``a-b`` and ``b-a`` count as the
        same connection.

        Args:
            connections: Pairs already accepted.
            connection: Pair being checked.

        Returns:
            True when the connection is new, False when it repeats
            one of ``connections``.
        """
        for conn in connections:
            res = conn.intersection(connection)
            if len(res) == 2:
                return False
        return True

    def _unique_coord_hub(self, data: list[str]) -> tuple[bool, int, str]:
        """Check that no two zones sit on the same coordinates.

        Connection and fleet size lines are skipped, blanks and
        comments too.

        Args:
            data: Lines of the map file.

        Returns:
            A ``(ok, line, message)`` triplet pointing at the first
            unreadable or repeated pair of coordinates.
        """
        coords: set[tuple[int, int]] = set()
        index = 1
        for line in data:
            if self._ignore_hashtag(line):
                index += 1
                continue
            if self._skip_line(line):
                index += 1
                continue
            if self._get_first_key(line) == "connection":
                index += 1
                continue
            if self._get_first_key(line) == "nb_drones":
                index += 1
                continue
            coord = self._get_coord_in_line(line)
            if coord[0] is False:
                return (False, index, "Something wrong on this line")
            if coord[1] in coords:
                return (False, index, "the coord is not unique")
            coords.add(coord[1])
            index += 1
        return (True, index, "")

    def _is_key_valid(self, data: list[str]) -> tuple[bool, int, str]:
        """Check that every line opens with a known key.

        Args:
            data: Lines of the map file.

        Returns:
            A ``(ok, line, message)`` triplet pointing at the first
            line whose key is none of ``hub``, ``start_hub``,
            ``end_hub``, ``connection`` or ``nb_drones``.
        """
        keys = self._get_main_keys(data)
        index = 1
        verif_key = {
            KeyName.HUB.value,
            KeyName.START_HUB.value,
            KeyName.END_HUB.value,
            KeyName.CONNECTION.value,
            KeyName.NB_DRONES.value
        }
        for key in keys:
            if self._ignore_hashtag(key):
                index += 1
                continue
            if self._skip_line(key):
                index += 1
                continue
            if key not in verif_key:
                return (False, index, "The key is not valid")
            index += 1
        return (True, index, "")

    def parse_data(self) -> list[tuple[bool, int, str]]:
        """Validate the whole map file and report every problem.

        Runs in two passes. The first one checks the file as a whole,
        its keys, its unique zones and their coordinates, and gives
        up as soon as one of those fails, since the second pass would
        then report errors caused by the first ones. The second pass
        walks the lines and checks the fleet size declaration, the
        metadata blocks and the connections.

        Returns:
            One ``(ok, line, message)`` triplet per problem found,
            ``line`` counting from 1 across the whole file, blanks
            and comments included. An empty list means the map is
            valid.

        Raises:
            IndexError: If the pattern matches no file at all.
            OSError: If the file exists but cannot be read.
        """
        self._load_data_from_file()
        self.data = self.del_comment(self.data)
        connections: list[set[str]] = []
        error_log: list[tuple[bool, int, str]] = []
        key_name = {
            HubName.START_HUB.value,
            HubName.END_HUB.value,
            HubName.HUB.value,
        }
        metadata_key_hub = {
            NameMetaData.ZONE.value,
            NameMetaData.MAX_D.value,
            NameMetaData.COLOR.value
        }
        metadata_key_conn = {
            NameMetaDataC.MAX_LINK.value
        }
        index = 0
        true_index = 1
        signal_drones = True

        error_log.append(self._unique_hub(self.data, HubName.START_HUB.value))
        error_log.append(self._unique_hub(self.data, HubName.END_HUB.value))
        error_log.append(self._start_end_present(self.data))
        error_log.append(self._is_len_split_two_point(self.data))
        error_log.append(self._is_key_valid(self.data))
        error_log.append(self._unique_name_hub(self.data))
        error_log.append(self._unique_coord_hub(self.data))
        error_log = [tup for tup in error_log if tup[0] is False]
        if len(error_log) > 0:
            return error_log
        names_hub = self._get_names_hub()

        for line in self.data:
            if self._skip_line(line):
                true_index += 1
                continue
            if self._ignore_hashtag(line):
                true_index += 1
                continue
            if index == 0 and signal_drones:
                signal_drones = False
                if not self._first_line(line, index):
                    error_log.append((False, true_index,
                                      "the nb drone is not "
                                      "present on the first line"))
                    continue
            else:
                key = self._get_first_key(line)
                if key in key_name:
                    if self._there_is_metadata(line):
                        res_m = self._get_metadata_in_line(line)
                        if res_m[0] is False:
                            error_log.append((False, true_index,
                                              "Something is wrong in"
                                              " this metadata"))
                            continue
                        res_mp = self._parse_metadata(res_m[1],
                                                      metadata_key_hub)
                        if res_mp is False:
                            error_log.append((False, true_index,
                                              "The key in metadata is wrong"))
                            continue
                elif key == "connection":
                    res_cn = self._parse_data_connection(line)
                    if res_cn[0] is False:
                        error_log.append((False, true_index,
                                          "There is an error in the "
                                          "connection"))
                        continue
                    res_ce = self._connection_names_exist(names_hub, res_cn[1])
                    if res_ce is False:
                        error_log.append((False, true_index,
                                          "Something is wrong with the name"))
                        continue
                    res_uc = self._uniq_connection(connections, res_cn[1])
                    if res_uc is False:
                        error_log.append((False, true_index,
                                          "The connection is not uniq"))
                        continue
                    connections.append(res_cn[1])
                    if self._there_is_metadata(line):
                        res_m = self._get_metadata_in_line(line)
                        if res_m[0] is False:
                            error_log.append((False, true_index,
                                              "Something is wrong"
                                              " in this metadata"))
                            continue
                        res_mp = self._parse_metadata(res_m[1],
                                                      metadata_key_conn)
                        if res_mp is False:
                            error_log.append((False, true_index,
                                              "Something is wrong "
                                              "in the key metadata"))
                            continue
            index += 1
            true_index += 1
        return error_log
