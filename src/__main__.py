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
        # is_graph = flag_manager.is_graphed()
        error_log = parsing.parse_data()
        translator.translate()
        graph._load_nodes(translator.hubs)
        graph._load_edges(translator.connections)
        print(graph.edges)
        print(graph.nodes)
        # print(is_graph)
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
