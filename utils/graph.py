from enum import Enum
from utils import Connection, Hub
import heapq
import itertools


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ColorType(Enum):
    BLUE = 'blue'
    ORANGE = 'orange'
    GREEN = 'green'
    RED = 'red'
    PURPLE = 'purple'
    BROWN = 'brown'
    PINK = 'pink'
    GRAY = 'gray'
    OLIVE = 'olive'
    CYAN = 'cyan'
    BLACK = 'black'
    YELLOW = 'yellow'
    LIME = 'lime'
    GOLD = 'gold'
    MAROON = 'maroon'
    DARKRED = 'darkred'
    CRIMSOM = 'crimson'


class Node:
    def __init__(self, name: str, coord: tuple[int, int], color: str,
                 max_drones: int, zone_type: str, type_hub: str) -> None:
        self.name = name
        self.coord = coord
        self.color: str = color
        self.max_drones = max_drones
        self.zone_type = ZoneType(zone_type)
        self.start = False
        self.end = False
        if type_hub == "start_hub":
            self.start = True
        if type_hub == "end_hub":
            self.end = True

    def entry_cost(self) -> int:
        if self.start is True:
            return (0)
        if (self.zone_type == ZoneType.RESTRICTED):
            return (2)
        return (1)

    def print_node(self) -> None:
        print(f"Name: {self.name}")
        print(f"Coord: {self.coord}")
        print(f"Color: {self.color}")
        print(f"Max_drones: {self.max_drones}")
        print(f"Zone Type: {self.zone_type.value}")
        print(f"is start: {self.start}")
        print(f"is end: {self.end}")


class Edge:
    def __init__(self, dst: str, max_link: int) -> None:
        self.dst = dst
        self.max_link = max_link

    def print_edge(self) -> None:
        print(f"dest: {self.dst}")
        print(f"max_link: {self.max_link}")


class Path_Finder:
    def __init__(self, pathing: list[str], turns: int, prio: int):
        self.pathing: list[str] = pathing
        self.turns: int = turns
        self.priority_count: int = prio


class Graph:
    def __init__(self, total_drones: int):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.total_drones = total_drones

    def load_edges(self, connections: list[Connection]) -> None:
        for connection in connections:
            a, b = connection.name_hub1, connection.name_hub2
            if a not in self.nodes or b not in self.nodes:
                continue
            if a not in self.edges:
                self.edges.setdefault(a, [])
            if b not in self.edges:
                self.edges.setdefault(b, [])
            self.edges[a].append(Edge(b, connection.max_link))
            self.edges[b].append(Edge(a, connection.max_link))

    def set_color(self, color: str) -> str:
        try:
            ColorType(color)
            return color
        except ValueError:
            return "gray"

    def load_nodes(self, hubs: list[Hub]) -> None:
        for hub in hubs:
            node = Node(
                hub.name,
                hub.coord,
                self.set_color(hub.color),
                hub.max_drones,
                hub.zone,
                hub.type_hub
            )
            if hub.zone == ZoneType.BLOCKED.value:
                continue
            self.nodes[hub.name] = node

    def debug_nodes(self) -> None:
        for key, node in self.nodes.items():
            print("=======================")
            print(key.upper())
            node.print_node()

    def debug_edges(self) -> None:
        for key, edges in self.edges.items():
            print("=======================")
            print(f"Origin: {key}")
            for edge in edges:
                edge.print_edge()

    def get_node(self, name: str) -> Node:
        return self.nodes[name]

    def get_start(self) -> Node:
        for node in self.nodes.values():
            if node.start is True:
                return node
        return node

    def get_end(self) -> Node:
        for node in self.nodes.values():
            if node.end is True:
                return node
        return node

    def get_neighbors(self, name: str) -> list[Edge]:
        return self.edges[name]

    def dijkstra_alg(self) -> Path_Finder:
        start, end = self.get_start(), self.get_end()
        dist: dict[str, float] = {name: float("inf")
                                  for name in self.nodes.keys()}
        prio_cnt: dict[str, int] = {name: 0 for name in self.nodes.keys()}
        previous: dict[str, str] = {}
        settled: set[str] = set()
        tie = itertools.count()
        dist[start.name] = 0
        heap: list[tuple[float, int, int, str]] = [
            (start.entry_cost(), 0, next(tie), start.name)
        ]

        while heap:
            cost_actual, _, _, name_actual = heapq.heappop(heap)
            if name_actual in settled:
                continue
            settled.add(name_actual)
            if name_actual == end.name:
                break
            for edge in self.edges[name_actual]:
                next_hub = edge.dst
                if next_hub in settled:
                    continue
                n_entry_cost = self.nodes[next_hub].entry_cost()
                n_cost = n_entry_cost + cost_actual
                n_prio = prio_cnt[name_actual] + (1 if self.nodes[name_actual].
                                                  zone_type == ZoneType.
                                                  PRIORITY else 0)
                if (n_cost, -n_prio) < (dist[next_hub], -prio_cnt[next_hub]):
                    dist[next_hub] = n_cost
                    previous.setdefault(next_hub, name_actual)
                    prio_cnt[next_hub] = n_prio
                    heapq.heappush(heap, (dist[next_hub], n_prio, next(tie),
                                          next_hub))
        if dist[end.name] == float("inf"):
            raise ValueError("No Path possible")
        return Path_Finder(
            pathing=self._get_path(previous),
            turns=int(dist[end.name]),
            prio=prio_cnt[end.name]
        )

    def _get_path(self, prev: dict[str, str]) -> list[str]:
        end = self.get_end()
        start = self.get_start()
        path: list[str] = []
        current = end.name
        while current != start.name:
            path.append(current)
            current = prev[current]
        path.append(start.name)
        path.reverse()
        return path

    def path_cost(self, path: list[str]) -> int:
        cost = 0
        for node in path:
            if self.nodes[node].start:
                continue
            cost += self.nodes[node].entry_cost()
        return cost

    def _get_nb_drone_min(self, path: list[str]) -> int:
        nb_max = float("inf")
        for node in path:
            if self.nodes[node].start:
                continue
            nb_max = min(self.nodes[node].max_drones, nb_max)
        for i in range(len(path)):
            if i < len(path) - 1:
                for edge in self.edges[path[i]]:
                    if edge.dst == path[i + 1]:
                        nb_max = min(nb_max, edge.max_link)
        return int(nb_max)

    def calcul_max_turns(self, paths: list[list[str]]) -> list[int]:
        count_d = [0] * len(paths)
        turn_paths = [self.path_cost(path) for path in paths]
        for _ in range(self.total_drones):
            i = min(range(len(paths)), key=lambda j: turn_paths[j] +
                    count_d[j])
            count_d[i] += 1
        return count_d
