from utils import Drone
from utils import Graph
from utils import ZoneType


Frame = list[tuple[int, tuple[float, float], bool]]


class Simulator:
    """Turn-by-turn drone routing simulation.

    Besides printing the moves of every turn, the simulator records a
    positional history (:attr:`history`) that the visualizer replays.
    """

    def __init__(self) -> None:
        self.drones: list[Drone] = []
        self.history: list[Frame] = []

    def load_drones(self, paths: list[list[str]], count_d: list[int]) -> None:
        id = 0
        j = 0
        for i in count_d:
            for _ in range(i):
                self.drones.append(Drone(id, paths[j]))
                id += 1
            j += 1

    def _is_every_drones_delivered(self) -> bool:
        for drone in self.drones:
            if drone.delivered is False:
                return False
        return True

    def _max_link(self, graph: Graph, src: str, dst: str) -> int:
        for node in graph.edges[src]:
            if node.dst == dst:
                return node.max_link
        return 0

    def _init_link_(self, link_usage: dict[str, dict[str, int]],
                    src: str, dest: str) -> None:
        link_usage.setdefault(src, {})
        link_usage[src].setdefault(dest, 0)

    def _init_occupancy(self, occupancy: dict[str, int], dest: str) -> None:
        occupancy.setdefault(dest, 0)

    def _check_link(self, graph: Graph, src: str, dest: str,
                    link_usage: dict[str, dict[str, int]]) -> bool:
        if link_usage[src][dest] >= self._max_link(graph, src, dest):
            return False
        return True

    def _check_hub(self, dest: str, graph: Graph,
                   occupancy: dict[str, int]) -> bool:
        if dest not in occupancy:
            self._init_occupancy(occupancy, dest)
        if occupancy[dest] >= graph.nodes[dest].max_drones:
            return False
        return True

    def _print_turn(self, moves: list[str]) -> None:
        """Print all moves of a turn on a single space-separated line.

        Follows the output format of section VII.5 of the subject: one
        line per turn, drones that do not move are omitted.
        """
        print(" ".join(moves))

    def _drone_coord(self, graph: Graph,
                     drone: Drone) -> tuple[float, float]:
        """Return the coordinate of a drone for the current snapshot.

        A delivered drone sits on the end zone, an in-flight drone is
        placed on the middle of the connection it is crossing, and a
        grounded drone is on its current zone.
        """
        if drone.delivered:
            end = graph.get_end().coord
            return (float(end[0]), float(end[1]))
        if drone.in_flight:
            src = graph.nodes[drone.path[drone.index]].coord
            dst = graph.nodes[drone.path[drone.index + 1]].coord
            return ((src[0] + dst[0]) / 2, (src[1] + dst[1]) / 2)
        pos = graph.nodes[drone.path[drone.index]].coord
        return (float(pos[0]), float(pos[1]))

    def _snapshot(self, graph: Graph) -> Frame:
        """Capture the position and delivered flag of every drone."""
        frame: Frame = []
        for drone in self.drones:
            frame.append((drone.id, self._drone_coord(graph, drone),
                          drone.delivered))
        return frame

    def run(self, graph: Graph) -> int:
        turns = 0
        self.history.append(self._snapshot(graph))
        while self._is_every_drones_delivered() is False:
            moves: list[str] = []
            occupancy: dict[str, int] = {}
            link_usage: dict[str, dict[str, int]] = {}
            self.drones = sorted(self.drones, key=lambda j: j.index,
                                 reverse=True)
            for drone in self.drones:
                if drone.delivered:
                    continue
                if drone.in_flight:
                    drone.index += 1
                    drone.in_flight = False
                    dest = drone.path[drone.index]
                    moves.append(f"D{drone.id}-{dest}")
                    if dest not in occupancy:
                        self._init_occupancy(occupancy, dest)
                    occupancy[dest] += 1
                    if dest == graph.get_end().name:
                        drone.delivered = True
                        continue
                else:
                    dest = drone.path[drone.index + 1]
                    src = drone.path[drone.index]
                    if src not in link_usage:
                        self._init_link_(link_usage, src, dest)
                    if dest not in link_usage[src]:
                        link_usage[src].setdefault(dest, 0)
                    if (self._check_link(graph, src, dest, link_usage)
                       and self._check_hub(dest, graph, occupancy)):
                        if graph.nodes[dest].zone_type == ZoneType.RESTRICTED:
                            link_usage[src][dest] += 1
                            drone.in_flight = True
                            moves.append(f"D{drone.id}-{src}-{dest}")
                            continue
                        else:
                            drone.index += 1
                            link_usage[src][dest] += 1
                            if dest not in occupancy:
                                self._init_occupancy(occupancy, dest)
                            occupancy[dest] += 1
                            if dest == graph.get_end().name:
                                drone.delivered = True
                            moves.append(f"D{drone.id}-{dest}")
                    else:
                        if src not in occupancy:
                            self._init_occupancy(occupancy, src)
                        occupancy[src] += 1
            self._print_turn(moves)
            turns += 1
            self.history.append(self._snapshot(graph))
        return turns
