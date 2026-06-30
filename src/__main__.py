from utils import FlagManager, Parsing, Translator
from utils import Graph


def main() -> None:
    try:
        flag_manager = FlagManager()
        flag_manager.init_args(None)
        path_file = flag_manager.get_path_from_flag()
        parsing = Parsing(path_file)
        translator = Translator(path_file)
        graph = Graph()
        error_log = parsing.parse_data()
        translator.translate()
        graph.load_nodes(translator.hubs)
        graph.load_edges(translator.connections)
        path_finder = graph.short_path()
        print(path_finder.pathing)
        print(error_log)
        print("===============================")
        # parsing._print_data()
        print("Hello from fly-in!")
    except ValueError as e:
        print("=======VALUE==ERROR========")
        print(f"Message : {e}")
        print("===========================")
    except (FileNotFoundError, PermissionError) as e:
        print("=======FILE===ERROR========")
        print(f"Message : {e}")
        print("===========================")


if __name__ == "__main__":
    main()
