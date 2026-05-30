from glob import glob


class Parsing():
    def __init__(self, path: str) -> None:
        self.path = path

    def load_data_from_file(self) -> None:
        path = self.path
        path_list = glob(path)
        path_extend = path_list[0]
        with open(path_extend, "r") as f:
            print(f.read())
