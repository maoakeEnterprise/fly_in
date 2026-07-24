import os

from utils import FlagManager, Parsing, Translator
from utils import Graph, ResidualGraph
from utils import Simulator


def main() -> None:
    try:
        flag_manager = FlagManager()
        flag_manager.init_args(None)
        path_file = flag_manager.get_path_from_flag()
        parsing = Parsing(path_file)
        translator = Translator(path_file)
        error_log = parsing.parse_data()
        if error_log:
            for _, line in error_log:
                print(f"Parsing error near line {line}")
            return
        translator.translate()
        graph = Graph(translator.nb_drones)
        graph.load_nodes(translator.hubs)
        graph.load_edges(translator.connections)

        residuals = ResidualGraph()
        residuals.build_residual(graph)
        residuals.maxflow(residuals.start_path, residuals.end_path)
        res = residuals.decompose(residuals.start_path, residuals.end_path)

        simulator = Simulator()
        simulator.load_drones(res, graph.calcul_max_turns(res))
        turns = simulator.run(graph)
        print(f"=== Simulation finished in {turns} turns ===")
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
