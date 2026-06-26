from enum import Enum
from utils import Connection, Hub


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class NameColor(Enum):
    RED = "red"
    YELLOW = "yellow"
    PURPLE = "purple"
    PINK = "pink"
    ORANGE = "orange"
    BLUE = "blue"


class Node:
    def __init__(self, name: str, coord: tuple[int, int], color: str,
                 max_drones: int, zone_type: str) -> None:
        self.name = name
        self.coord = coord
        self.color = NameColor(color)
        self.max_drones = max_drones
        self.zone_type = ZoneType(zone_type)
        self.start = False
        self.end = False
        if name == "start_hub":
            self.start = True
        if name == "end_hub":
            self.end = True

    def entry_cost(self) -> int:
        if (self.zone_type == ZoneType.RESTRICTED):
            return (2)
        return (1)


class Edge:
    def __init__(self, dst: str, max_link: str) -> None:
        self.dst = dst
        self.max_link = max_link


class Graph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}

    def _load_edges(self, connections: list[Connection]) -> None:
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

    def _load_nodes(self, hubs: list[Hub]) -> None:
        for hub in hubs:
            node = Node(
                hub.name,
                hub.coord,
                hub.color,
                hub.max_drones,
                hub.zone
            )
            if hub.zone == ZoneType.BLOCKED.value:
                continue
            self.nodes[hub.name] = node

    def get_neighbors(self, name: str) -> Node:
        return self.nodes[name]

    def get_edge(self, name: str) -> list[Edge]:
        return self.edges[name]
