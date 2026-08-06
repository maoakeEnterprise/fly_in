"""Graph interface of the Fly-in simulator.

Builds the zone network out of ``Node`` and ``Edge`` objects and finds
the cheapest route from the start zone to the end zone, which the
simulator then replays turn by turn.
"""
from enum import Enum
from utils import Connection, Hub
import heapq
import itertools


class ZoneType(Enum):
    """Movement cost class of a zone.

    ``restricted`` costs 2 turns to enter, ``blocked`` cannot be
    entered at all, ``normal`` and ``priority`` both cost 1 turn,
    ``priority`` being preferred on equal cost during pathfinding.
    """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ColorType(Enum):
    """Colors the visualizer knows how to draw.

    A zone whose color is missing from this enum falls back to gray,
    see :meth:`Graph.set_color`.
    """

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
    """A zone of the map, with its movement cost and its capacity.

    ``start`` and ``end`` are derived from the ``type_hub`` given at
    construction; that raw value is not kept as an attribute.

    Attributes:
        name: Unique zone name, used as key everywhere in the graph.
        coord: Position of the zone, used by the visualizer.
        color: Color to draw the zone with, already validated.
        max_drones: How many drones may sit on the zone at once.
        zone_type: Cost class of the zone, see :class:`ZoneType`.
        start: True if the fleet takes off from this zone.
        end: True if this zone is the delivery target.
    """

    def __init__(self, name: str, coord: tuple[int, int], color: str,
                 max_drones: int, zone_type: str, type_hub: str,
                 total_drones: int) -> None:
        """Build a zone and derive its start and end flags.

        Args:
            name: Unique zone name.
            coord: Position of the zone on the map.
            color: Color to draw the zone with.
            max_drones: Simultaneous drone capacity of the zone.
            zone_type: One of the :class:`ZoneType` values.
            type_hub: ``"start_hub"``, ``"end_hub"`` or ``"hub"``.

        Raises:
            ValueError: If ``zone_type`` is not a known zone type.
        """
        self.name = name
        self.coord = coord
        self.color: str = color
        self.max_drones = max_drones
        self.zone_type = ZoneType(zone_type)
        self.start = False
        self.end = False
        if type_hub == "start_hub":
            self.start = True
            self.max_drones = total_drones
        if type_hub == "end_hub":
            self.end = True
            self.max_drones = total_drones

    def entry_cost(self) -> int:
        """Give the number of turns needed to enter this zone.

        Returns:
            0 for the start zone, since the fleet is already there,
            2 for a restricted zone, and 1 for any other zone. This
            is the weight :meth:`Graph.dijkstra_alg` sums up.
        """
        if self.start is True:
            return (0)
        if (self.zone_type == ZoneType.RESTRICTED):
            return (2)
        return (1)

    def print_node(self) -> None:
        """Print every field of the zone, for debugging."""
        print(f"Name: {self.name}")
        print(f"Coord: {self.coord}")
        print(f"Color: {self.color}")
        print(f"Max_drones: {self.max_drones}")
        print(f"Zone Type: {self.zone_type.value}")
        print(f"is start: {self.start}")
        print(f"is end: {self.end}")


class Edge:
    """One direction of a connection between two zones.

    A map connection is bidirectional, so the loaders store it as two
    ``Edge`` objects, one in each adjacency list.

    Attributes:
        dst: Name of the zone this edge leads to.
        max_link: How many drones may cross the connection at once.
    """

    def __init__(self, dst: str, max_link: int) -> None:
        """Build an edge leading to ``dst``.

        Args:
            dst: Name of the destination zone.
            max_link: Simultaneous capacity of the connection.
        """
        self.dst = dst
        self.max_link = max_link

    def print_edge(self) -> None:
        """Print the destination and capacity, for debugging."""
        print(f"dest: {self.dst}")
        print(f"max_link: {self.max_link}")


class Path_Finder:
    """Result of a pathfinding run, consumed by the simulator.

    Attributes:
        pathing: Ordered zone names, start first and end last.
        turns: Total entry cost of ``pathing``, in turns, for a
            single drone flying it alone.
        priority_count: How many priority zones the route crosses,
            used to break ties between routes of equal cost.
    """

    def __init__(self, pathing: list[str], turns: int, prio: int):
        """Store the outcome of a pathfinding run.

        Args:
            pathing: Ordered zone names from start to end.
            turns: Total entry cost of the route.
            prio: Number of priority zones crossed.
        """
        self.pathing: list[str] = pathing
        self.turns: int = turns
        self.priority_count: int = prio


class Graph:
    """Zone network the drones fly through.

    Two views of the map are kept. nodes and edges exclude the
    blocked zones and are what the pathfinding walks; complete_nodes
    and complete_edges keep every zone so the visualizer can still
    draw the blocked ones.

    Attributes:
        nodes: Traversable zones indexed by name.
        edges: Adjacency list over nodes, both directions stored.
        complete_nodes: Every zone, blocked ones included.
        complete_edges: Adjacency list over complete_nodes.
        total_drones: Fleet size read from nb_drones.
    """
    def __init__(self, total_drones: int):
        """Create an empty graph for a fleet of total_drones."""
        self.nodes: dict[str, Node] = {}
        self.complete_nodes: dict[str, Node] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.complete_edges: dict[str, list[Edge]] = {}
        self.total_drones = total_drones

    def load_edges(self, connections: list[Connection]) -> None:
        """Fill the traversable adjacency list.

        Both directions are stored. A connection is skipped when
        either end is missing from ``nodes``, which is how blocked
        zones get cut out of the pathfinding graph, so
        :meth:`load_nodes` must run first.

        Args:
            connections: Parsed connections to turn into edges.
        """
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

    def load_commplete_edges(self, connections: list[Connection]) -> None:
        """Fill the adjacency list that keeps the blocked zones.

        Same work as :meth:`load_edges` but over ``complete_nodes``,
        so the visualizer can still draw the connections leading to
        blocked zones. :meth:`load_nodes` must run first.

        Args:
            connections: Parsed connections to turn into edges.
        """
        for connection in connections:
            a, b = connection.name_hub1, connection.name_hub2
            if a not in self.complete_nodes or b not in self.complete_nodes:
                continue
            if a not in self.complete_edges:
                self.complete_edges.setdefault(a, [])
            if b not in self.complete_edges:
                self.complete_edges.setdefault(b, [])
            self.complete_edges[a].append(Edge(b, connection.max_link))
            self.complete_edges[b].append(Edge(a, connection.max_link))

    def set_color(self, color: str) -> str:
        """Keep a color the visualizer supports, or fall back to gray.

        Args:
            color: Color read from the map file, possibly empty or
                unsupported.

        Returns:
            ``color`` itself when it belongs to :class:`ColorType`,
            ``"gray"`` otherwise.
        """
        try:
            ColorType(color)
            return color
        except ValueError:
            return "gray"

    def load_nodes(self, hubs: list[Hub]) -> None:
        """Turn the parsed zones into nodes of the graph.

        Every zone lands in ``complete_nodes``; blocked ones are kept
        out of ``nodes`` so the pathfinding never walks them.

        Args:
            hubs: Zones produced by the translator.
        """
        for hub in hubs:
            node = Node(
                hub.name,
                hub.coord,
                self.set_color(hub.color),
                hub.max_drones,
                hub.zone,
                hub.type_hub,
                self.total_drones
            )
            self.complete_nodes[hub.name] = node
            if hub.zone == ZoneType.BLOCKED.value:
                continue
            self.nodes[hub.name] = node

    def debug_nodes(self) -> None:
        """Print every traversable node, for debugging."""
        for key, node in self.nodes.items():
            print("=======================")
            print(key.upper())
            node.print_node()

    def debug_edges(self) -> None:
        """Print every edge grouped by origin zone, for debugging."""
        for key, edges in self.edges.items():
            print("=======================")
            print(f"Origin: {key}")
            for edge in edges:
                edge.print_edge()

    def get_node(self, name: str) -> Node:
        """Look up a traversable zone by its name.

        Args:
            name: Zone name to look up.

        Returns:
            The matching node.

        Raises:
            KeyError: If no traversable zone carries that name, which
                covers the case of a blocked zone.
        """
        return self.nodes[name]

    def get_start(self) -> Node:
        """Find the zone the fleet takes off from.

        Returns:
            The node whose ``start`` flag is set. The parser
            guarantees exactly one such zone; were none flagged, the
            last node visited would be returned instead.

        Raises:
            UnboundLocalError: If the graph holds no traversable zone
                at all, leaving the fallback nothing to return.
        """
        for node in self.nodes.values():
            if node.start is True:
                return node
        return node

    def get_end(self) -> Node:
        """Find the zone the drones must be delivered to.

        Returns:
            The node whose ``end`` flag is set. The parser guarantees
            exactly one such zone; were none flagged, the last node
            visited would be returned instead.

        Raises:
            UnboundLocalError: If the graph holds no traversable zone
                at all, leaving the fallback nothing to return.
        """
        for node in self.nodes.values():
            if node.end is True:
                return node
        return node

    def get_neighbors(self, name: str) -> list[Edge]:
        """List the edges leaving a zone.

        Args:
            name: Name of the zone whose neighbors are wanted.

        Returns:
            One edge per connection leaving the zone, in load order.

        Raises:
            KeyError: If the zone is unknown or carries no
                connection at all.
        """
        return self.edges[name]

    def get_node_from_coord(self, coord: tuple[float, float]) -> Node | None:
        """Find the zone sitting at a position.

        Reverse lookup used by the visualizer, which knows where a
        drone is drawn but not which zone it stands on. The search runs
        over ``complete_nodes``, so a blocked zone is matched too, and
        the integer coordinates of the map are compared as floats
        because the simulator works in floats.

        Args:
            coord: Position to match, exactly as the simulator
                reports it.

        Returns:
            The node standing at that position, or None if the
            position falls between two zones, which means the drone is
            flying over a link rather than parked.
        """
        for _, node in self.complete_nodes.items():
            x_int, y_int = node.coord
            coord_test = (float(x_int), float(y_int))
            if coord_test == coord:
                return node
        return None

    def get_edge_from_coord(self, coord: tuple[float, float]
                            ) -> tuple[str, Edge] | None:
        """Find the link a drone in flight is halfway along.

        Counterpart of :meth:`get_node_from_coord` for the positions it
        rejects: a drone crossing a restricted link is drawn at the
        midpoint of the two zones, so the midpoint of every connection
        is recomputed and compared to the position. Each connection is
        stored in both directions, so the first orientation that
        matches is the one returned.

        Args:
            coord: Position to match, expected to be the midpoint of a
                connection.

        Returns:
            The name of the source zone paired with the edge leaving
            it, or None if no link has that midpoint.
        """
        for name, listedges in self.complete_edges.items():
            x1, y1 = self.complete_nodes[name].coord
            for edge in listedges:
                dst = edge.dst
                x2, y2 = self.complete_nodes[dst].coord
                res = ((x1 + x2) / 2, (y1 + y2) / 2)
                if res == coord:
                    return (name, edge)
        return None

    def dijkstra_alg(self) -> Path_Finder:
        """Find the cheapest route from the start zone to the end one.

        Weights come from :meth:`Node.entry_cost`, so a restricted
        zone counts double. Ties on cost are settled in favour of the
        route crossing the most priority zones, then by insertion
        order so the heap comparison stays total.

        Returns:
            A :class:`Path_Finder` holding the ordered zone names,
            the total cost in turns, and the number of priority zones
            the route crosses.

        Raises:
            ValueError: If the end zone stays unreachable, its
                distance still infinite once the heap is empty.
        """
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
        """Rebuild the route out of the predecessor table.

        Walks backwards from the end zone up to the start one, then
        flips the result.

        Args:
            prev: Table mapping each zone to the zone it was first
                reached from, as filled by :meth:`dijkstra_alg`.

        Returns:
            Ordered zone names, start first and end last.

        Raises:
            KeyError: If the chain breaks before reaching the start
                zone, meaning ``prev`` does not cover the route.
        """
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
        """Sum the entry costs along a route.

        The start zone is skipped, since the fleet is already there.

        Args:
            path: Ordered zone names, as returned by
                :meth:`_get_path`.

        Returns:
            Number of turns one drone needs to fly the whole route
            on its own.
        """
        cost = 0
        for node in path:
            if self.nodes[node].start:
                continue
            cost += self.nodes[node].entry_cost()
        return cost

    def _get_nb_drone_min(self, path: list[str]) -> int:
        """Give the narrowest capacity found along a route.

        Zone capacities and connection capacities are both taken into
        account, the start zone excepted since it holds the whole
        fleet at once.

        Args:
            path: Ordered zone names to measure.

        Returns:
            How many drones the route can carry side by side, that is
            the smallest ``max_drones`` or ``max_link`` on it.
        """
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

    def spread_drones(self, paths: list[list[str]]) -> list[int]:
        """Share the fleet between routes to land as early as
        possible.

        Drones are handed out one at a time to the route with the
        lowest projected arrival, that is its cost plus the drones
        already queued on it, which assumes a single drone enters a
        route per turn.

        Args:
            paths: Candidate routes, each an ordered list of zone
                names.

        Returns:
            How many drones to send on each route, aligned on
            ``paths``; the values sum up to ``total_drones``.
        """
        count_d = [0] * len(paths)
        turn_paths = [self.path_cost(path) for path in paths]
        for _ in range(self.total_drones):
            i = min(range(len(paths)), key=lambda j: turn_paths[j] +
                    count_d[j])
            count_d[i] += 1
        return count_d
