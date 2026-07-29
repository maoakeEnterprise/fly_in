from utils import FlagManager, Parsing, Translator
from utils import Graph
from utils import Simulator, Visualizer


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
        graph.load_commplete_edges(translator.connections)
        pathfinder = graph.dijkstra_alg()

        simulator = Simulator()
        simulator.load_drones([pathfinder.pathing],
                              graph.calcul_max_turns([pathfinder.pathing]))
        turns = simulator.run(graph)
        vizualiser = Visualizer(graph, simulator.history, interval=800)
        vizualiser.render()
        print(f"=== Simulation finished in {turns} turns ===")
    except ValueError as e:
        print("=======VALUE==ERROR========")
        print(f"Message : {e}")
        print("===========================")
    except (FileNotFoundError, PermissionError) as e:
        print("=======FILE===ERROR========")
        print(f"Message : {e}")
        print("===========================")
    except Exception as e:
        print("======UNKNOW=====ERROR=====")
        print(f"Message: {e}")
        print("===========================")
    except KeyboardInterrupt as e:
        print("===========================")
        print(f"Message: {e}")
        print("===========================")


if __name__ == "__main__":
    main()
