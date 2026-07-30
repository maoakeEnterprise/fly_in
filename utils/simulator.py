from utils import Drone
from utils import Graph
from utils import ZoneType

"""
    make an object to who get the a list of tuple in this tuple he will
    get the id drone, the coord in float, and a bool to know if he is delivered
    or not
"""
Frame = list[tuple[int, tuple[float, float], bool]]


class Simulator:
    """simulation to follow every drone turn by turn
       drone will help to follow the turns
       history will help for the vizualizer
    """

    def __init__(self) -> None:
        self.drones: list[Drone] = []
        self.history: list[Frame] = []

    def load_drones(self, paths: list[list[str]], count_d: list[int]) -> None:
        """init every drone
        """
        id = 0
        j = 0
        for i in count_d:
            for _ in range(i):
                self.drones.append(Drone(id, paths[j]))
                id += 1
            j += 1

    def _is_every_drones_delivered(self) -> bool:
        """to know if every drone is in the end or not
        """
        for drone in self.drones:
            if drone.delivered is False:
                return False
        return True

    def _max_link(self, graph: Graph, src: str, dst: str) -> int:
        """get the max link on a link from src and dst
        """
        for node in graph.edges[src]:
            if node.dst == dst:
                return node.max_link
        return 0

    def _init_link_(self, link_usage: dict[str, dict[str, int]],
                    src: str, dest: str) -> None:
        """init the link usage to 0 cause no drone never be on this link
        """
        link_usage.setdefault(src, {})
        link_usage[src].setdefault(dest, 0)

    def _init_occupancy(self, occupancy: dict[str, int], dest: str) -> None:
        """ init the occupancy cause no drone never be on this hub
        """
        occupancy.setdefault(dest, 0)

    def _check_link(self, graph: Graph, src: str, dest: str,
                    link_usage: dict[str, dict[str, int]]) -> bool:
        """ return a bool to know if the link is saturate or not
        """
        if link_usage[src][dest] >= self._max_link(graph, src, dest):
            return False
        return True

    def _check_hub(self, dest: str, graph: Graph,
                   occupancy: dict[str, int]) -> bool:
        """ check a bool to know if the hub is saturate or not
        """
        if dest not in occupancy:
            self._init_occupancy(occupancy, dest)
        if occupancy[dest] >= graph.nodes[dest].max_drones:
            return False
        return True

    def _print_turn(self, moves: list[str]) -> None:
        """Print all move on the turn
        """
        print(" ".join(moves))

    def _drone_coord(self, graph: Graph,
                     drone: Drone) -> tuple[float, float]:
        """return the actual position on a drone we return float
           cause some drone can be on the link if he is on a restricted hub
           like this we divide by two from the src and the dst
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
        """snap the position and delivered flag of every drone."""
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
                       and self._check_hub(dest, graph, occupancy) and graph.nodes[dest].zone_type != ZoneType.RESTRICTED):
                        drone.index += 1
                        link_usage[src][dest] += 1
                        if dest not in occupancy:
                            self._init_occupancy(occupancy, dest)
                        occupancy[dest] += 1
                        if dest == graph.get_end().name:
                            drone.delivered = True
                        moves.append(f"D{drone.id}-{dest}")
                    elif (self._check_link(graph, src, dest, link_usage)
                                           and graph.nodes[dest].zone_type == ZoneType.RESTRICTED):
                        link_usage[src][dest] += 1
                        drone.in_flight = True
                        moves.append(f"D{drone.id}-{src}-{dest}")
                        continue
                    else:
                        if src not in occupancy:
                            self._init_occupancy(occupancy, src)
                        occupancy[src] += 1
            self._print_turn(moves)
            turns += 1
            self.history.append(self._snapshot(graph))
        return turns
