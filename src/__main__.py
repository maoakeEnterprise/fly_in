from utils import FlagManager, Parsing, Translator
from utils import Graph, ResidualGraph


def main() -> None:
    try:
        flag_manager = FlagManager()
        residuals = ResidualGraph()
        flag_manager.init_args(None)
        path_file = flag_manager.get_path_from_flag()
        parsing = Parsing(path_file)
        translator = Translator(path_file)
        error_log = parsing.parse_data()
        translator.translate()
        graph = Graph(translator.nb_drones)
        graph.load_nodes(translator.hubs)
        graph.load_edges(translator.connections)
        path_finder = graph.short_path()
        print(path_finder.pathing)
        residuals.build_residual(graph)
        residuals.maxflow(residuals.start_path, residuals.end_path)
        res = residuals.decompose(residuals.start_path, residuals.end_path)
        print(res)
        for path in res:
            print(graph.path_cost(path))
        print(graph.calcul_max_turns(res))
        print(error_log)
        print("===============================")
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
