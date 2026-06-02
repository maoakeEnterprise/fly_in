from glob import glob
from enum import Enum


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

    def _is_key_valid(self, data: list[str]) -> bool:
        keys = self._get_main_keys(data)
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
                return False
        return True

    def parsing_data(self) -> None:
        self._load_data_from_file()
        index = 0
        index_com = 1
        error_log: list[tuple[bool, int]] = []
        error_log.append(self._unique_hub(self.data, HubName.START_HUB.value))
        error_log.append(self._unique_hub(self.data, HubName.END_HUB.value))
        error_log.append(self._is_len_split_two_point(self.data))
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
