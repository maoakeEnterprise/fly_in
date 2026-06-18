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

    """
        Load the data forme the files with the path gived
    """
    def _load_data_from_file(self) -> None:
        data_str = ""
        path = self.path
        path_list = glob(path)
        path_extend = path_list[0]

        with open(path_extend, "r") as f:
            data_str = f.read()
            self.data = data_str.split("\n")

    """
        Print the data for some debug
    """
    def _print_data(self) -> None:
        self._load_data_from_file()
        for line in self.data:
            print(line)

    """
        Skip the line with # make like a commentary line
        If the # is on the same line like the connection hub or whatever he
        will not be ignored so be carefull about this
    """
    def _ignore_hashtag(self, line: str) -> bool:
        line_striped = line.strip()
        if line_striped.startswith("#"):
            return True
        return False

    """
        Verify if the first line is nb_drones
    """
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

    """
        Skip empty line with or whatever
    """
    def _skip_line(self, line: str) -> bool:
        line_strip = line.strip()
        if line_strip == "":
            return True
        return False

    """
        verify if hub is unique
    """
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

    """
        verify if the line is splitted in two
    """
    def _is_len_split_two_point(self, data: list[str]) -> tuple[bool, int]:
        index = 0
        for line in data:
            if self._skip_line(line):
                continue
            if self._ignore_hashtag(line):
                continue
            tab_l = line.split(":")
            if len(tab_l) != 2:
                return (False, index)
            index += 1
        return (True, index)

    """
        get the main keys in index 0
    """
    def _get_main_keys(self, data: list[str]) -> list[str]:
        keys = [line.split(":")[0] for line in data]
        return keys

    """
        check for the name after the two point if he is unique
    """
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

    """
        to get the first key in the split can be usefull
    """
    def _get_first_key(self, line: str) -> str:
        line_s = line.split(":")
        return line_s[0].strip()

    """
        get the name and verify if the name is normed
    """
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

    """
        get the coord in line and verify if its normed
    """
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
            return (False, (0, 0))
        return (True, (int(list_int[0]), int(list_int[1])))

    """
        verify if the metada is normed or not in the extern not in detail
    """
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

    """
        verify the keys in the metadata
    """
    def _parse_metadata(self, metadata: str, keys: list[str]) -> bool:
        data = metadata.strip().split(" ")
        keys_c = keys.copy()
        for tmp in data:
            k_v = tmp.split("=")
            if len(k_v) != 2:
                return False
            if k_v[0] in keys_c:
                keys_c.remove(k_v[0])
            else:
                return False
        return True

    """
        verify if there is some metadata
    """
    def _there_is_metadata(self, line: str) -> bool:
        line_s = line.split(":")
        name = line_s[0]
        index_md = 2 if name == "connection" else 3
        data = line_s[1].strip().split(" ")
        if len(data) < index_md + 1:
            return False
        return True

    """
        parse the data connection to see if he is normed and
        get the data connection
    """
    def _parse_data_connection(self, line: str) -> tuple[bool, set[str]]:
        conn_set = set()
        data = line.strip().split(":")[1].strip().split(" ")
        connection = data[0].split("-")
        if len(connection) != 2:
            return (False, conn_set)
        conn_set.add(connection[0])
        conn_set.add(connection[1])
        return (True, conn_set)

    """
        get a set of names hub
    """
    def _get_names_hub(self) -> set[str]:
        names = set()
        for line in self.data:
            names.add(self._get_name_in_line(line, 0)[2])
        return names

    """
        verify if the name exist in the connection proposed
    """
    def _connection_names_exist(self, names: set[str], connection: set[str]
                                ) -> bool:
        verif_set = names.intersection(connection)
        if len(verif_set) != 2:
            return False
        return True

    """
        verify if the connection already exist or not
        True if do not exist False if he exist
    """
    def _uniq_connection(self, connections: list[set[str]],
                         connection: set[str]) -> bool:
        for conn in connections:
            res = conn.intersection(connection)
            if len(res) == 2:
                return False
        return True

    """
        verify if the coord is unique or not
    """
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

    """
        verify if the key is valid or not
    """
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

    def parse_data(self) -> list[tuple[bool, int]]:
        self._load_data_from_file()
        error_log: list[tuple[bool, int]] = []
        key_name = {
            HubName.START_HUB.value,
            HubName.END_HUB.value,
            HubName.HUB,
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
        error_log.append(self._unique_hub(self.data, HubName.START_HUB.value))
        error_log.append(self._unique_hub(self.data, HubName.END_HUB.value))
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
            if index == 0:
                if not self._first_line(line, index):
                    error_log.append((False, true_index))
                    continue
            else:
                key = self._get_first_key(line)
                if key in key_name:
                    if self._there_is_metadata(line):
                        res_m = self._get_metadata_in_line(line)
                        if res_m[0] is False:
                            error_log.append((False, true_index))
                            continue
                        res_mp = self._parse_metadata(res_m[1],
                                                      metadata_key_hub)
                        if res_mp is False:
                            error_log.append((False, true_index))
                            continue
                elif key == "connection":
                    connections: list[set[str]] = []
                    res_cn = self._parse_data_connection(line)
                    if res_cn[0] is False:
                        error_log.append((False, true_index))
                        continue
                    res_ce = self._connection_names_exist(names_hub, res_cn[1])
                    if res_ce is False:
                        error_log.append((False, true_index))
                        continue
                    res_uc = self._uniq_connection(connections, res_cn[1])
                    if res_uc is False:
                        error_log.append((False, true_index))
                        continue
                    connections.append(res_cn[1])
                    if self._there_is_metadata(line):
                        res_m = self._get_metadata_in_line(line)
                        if res_m[0] is False:
                            error_log.append((False, true_index))
                            continue
                        res_mp = self._parse_metadata(res_m[1],
                                                      metadata_key_conn)
                        if res_mp is False:
                            error_log.append((False, true_index))
                            continue
            index += 1
            true_index += 1
        return error_log
