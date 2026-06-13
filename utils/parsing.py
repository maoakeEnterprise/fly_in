from glob import glob
from enum import Enum
import re


class HubName(Enum):
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"


class KeyName(Enum):
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    CONNECTION = "connection"
    NB_DRONES = "nb_drones"


class NameMetaData(Enum):
    ZONE = "zone"
    COLOR = "color"
    MAX_D = "max_drones"


class NameMetaDataC(Enum):
    MAX_LINK = "max_link_capacity"


class KeyNameZone(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


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
        line_strip = line.strip()
        if line_strip == "":
            return True
        return False

    def _unique_hub(self, data: list[str], name_hub: str) -> tuple[bool, int]:
        len_nh = 0
        index = 0
        for line in data:
            tab_l = line.split(":")
            new_l = tab_l[0].strip()
            if not new_l.startswith(name_hub) and name_hub in new_l:
                return (False, index)
            len_nh += line.count(name_hub)
            if len_nh > 1:
                return (False, index)
            index += 1
        return (True, index)

    def _is_len_split_two_point(self, data: list[str]) -> tuple[bool, int]:
        index = 0
        for line in data:
            tab_l = line.split(":")
            if len(tab_l) != 2:
                return (False, index)
            index += 1
        return (True, index)

    def _get_main_keys(self, data: list[str]) -> list[str]:
        keys = [line.split(":")[0] for line in data]
        return keys

    def _unique_name_hub(self, data: list[str]) -> tuple[bool, int]:
        names: set[str] = set()
        index = 0
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
            if res[0] is False and name in names:
                return (False, index)
            names.add(name)
        return (True, index)

    def _get_first_key(self, line: str) -> str:
        line_s = line.split(":")
        return line_s[0].strip()

    def _get_name_in_line(self, line: str, index: int
                          ) -> tuple[bool, int, str]:
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
                return (False, index, name)
            name = word
            break
        return (True, index, name)

    def _get_coord_in_line(self, line: str) -> tuple[bool, tuple[int, int]]:
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
            print(list_int)
            return (False, (0, 0))
        return (True, (int(list_int[0]), int(list_int[1])))

    # verify if the metada is normed or not in the extern not in detail
    def _get_metadata_in_line(self, line: str) -> tuple[bool, str]:
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

    # verify the keys in the metadata
    def _parse_metadata(self, metadata: str, keys: list[str]) -> bool:
        data = metadata.strip().split(" ")
        for tmp in data:
            k_v = tmp.split("=")
            if len(k_v) != 2:
                return False
            if k_v[0] in keys:
                keys.remove(k_v[0])
            else:
                return False
        return True

    # verify if there is some metadata
    def _there_is_metadata(self, line: str) -> int:
        line_s = line.split(":")
        name = line_s[0]
        index_md = 2 if name == "connection" else 3
        data = line_s[1].strip().split(" ")
        if len(data) < index_md + 1:
            return False
        return True

    def _parse_data_connection(self, line: str) -> tuple[bool, set[str]]:
        conn_set = set()
        data = line.strip().split(":")[1].strip().split(" ")
        connection = data[0].split("-")
        if len(connection) != 2:
            return (False, conn_set)
        conn_set.add(connection[0])
        conn_set.add(connection[1])
        return (True, conn_set)

    def _get_names_hub(self) -> set[str]:
        names = set()
        for line in self.data:
            names.add(self._get_name_in_line(line, 0)[2])
        return names

    def connection_names_exist(self, names: set[str], connection: set[str]
                               ) -> bool:
        verif_set = names.intersection(connection)
        if len(verif_set) != 2:
            return False
        return True

    def _uniq_connection(self, connections: list[set[str]],
                         connection: set[str]) -> bool:
        for conn in connections:
            res = conn.intersection(connection)
            if len(res) == 2:
                return False
        return True

    def _unique_coord_hub(self, data: list[str]) -> tuple[bool, int]:
        coords: set[tuple[int, int]] = set()
        index = 0
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
                return (False, index)
            if coord[1] in coords:
                return (False, index)
            coords.add(coord[1])
        return (True, index)

    def _is_key_valid(self, data: list[str]) -> tuple[bool, int]:
        keys = self._get_main_keys(data)
        index = 0
        verif_key = {
            KeyName.HUB.value,
            KeyName.START_HUB.value,
            KeyName.END_HUB.value,
            KeyName.CONNECTION.value,
            KeyName.NB_DRONES.value
        }
        for key in keys:
            if self._ignore_hashtag(key):
                continue
            if self._skip_line(key):
                continue
            if key not in verif_key:
                return (False, index)
            index += 1
        return (True, index)

    def parsing_data(self) -> None:
        self._load_data_from_file()
        index = 0
        index_com = 1
        error_log: list[tuple[bool, int]] = []
        error_log.append(self._unique_hub(self.data, HubName.START_HUB.value))
        error_log.append(self._unique_hub(self.data, HubName.END_HUB.value))
        error_log.append(self._is_len_split_two_point(self.data))
        error_log.append(self._is_key_valid(self.data))
        for line in self.data:
            if self._skip_line(line):
                index += 1
                continue
            if (self._ignore_hashtag(line)):
                index_com += 1
                continue
            if index == 0:
                if not self._first_line(line, index):
                    error_log.append((False, index))
            else:
                pass
            index += 1
