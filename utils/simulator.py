"""Turn by turn engine of the Fly-in simulator.

Takes the routes computed by :mod:`utils.graph`, spreads the fleet over
them and moves every drone one turn at a time while enforcing the zone
capacities and the link capacities. Each turn is printed on stdout and
kept in a history the visualizer replays afterwards.
"""
from utils import Drone
from utils import Graph
from utils import ZoneType

Frame = list[tuple[int, tuple[float, float], bool]]
"""State of the whole fleet at one turn.

One tuple per drone, holding its id, its position as floats, since a
drone flying over a restricted link sits halfway between two zones, and
whether it already reached the end zone.
"""


class Simulator:
    """Fleet mover, replaying every drone turn by turn.

    Attributes:
        drones: Fleet being moved, filled by :meth:`load_drones`. It is
            re-sorted at every turn so the drones closest to the end
            zone move first and free their spot.
        history: One :data:`Frame` per turn, plus the initial one, kept
            for the visualizer.
    """

    def __init__(self) -> None:
        """Build an empty simulator, with no drone and no history."""
        self.drones: list[Drone] = []
        self.history: list[Frame] = []

    def load_drones(self, paths: list[list[str]], count_d: list[int]) -> None:
        """Create the fleet, giving each drone the route it must follow.

        Drone ids are handed out in order, so the drones of the first
        path get the lowest ones.

        Args:
            paths: Routes to spread the fleet over, each one a list of
                zone names from the start zone to the end zone.
            count_d: How many drones to put on each path, aligned with
                ``paths``.
        """
        id = 0
        j = 0
        for i in count_d:
            for _ in range(i):
                self.drones.append(Drone(id, paths[j]))
                id += 1
            j += 1

    def _is_every_drones_delivered(self) -> bool:
        """Tell whether the whole fleet reached the end zone.

        Returns:
            True once every drone is delivered, which is what stops
            the loop of :meth:`run`.
        """
        for drone in self.drones:
            if drone.delivered is False:
                return False
        return True

    def _max_link(self, graph: Graph, src: str, dst: str) -> int:
        """Give how many drones may take a link at the same turn.

        Args:
            graph: Zone network holding the links.
            src: Zone the link starts from.
            dst: Zone the link goes to.

        Returns:
            The capacity of the link, or 0 if no link joins the two
            zones, which then forbids any move.
        """
        for node in graph.edges[src]:
            if node.dst == dst:
                return node.max_link
        return 0

    def _init_link_(self, link_usage: dict[str, dict[str, int]],
                    src: str, dest: str) -> None:
        """Start counting a link, no drone took it yet this turn.

        Args:
            link_usage: Per turn counter, keyed by source zone then by
                destination zone. Modified in place.
            src: Zone the link starts from.
            dest: Zone the link goes to.
        """
        link_usage.setdefault(src, {})
        link_usage[src].setdefault(dest, 0)

    def _init_occupancy(self, occupancy: dict[str, int], dest: str) -> None:
        """Start counting a zone, no drone sits on it yet this turn.

        Args:
            occupancy: Per turn counter, keyed by zone name. Modified
                in place.
            dest: Zone to start counting.
        """
        occupancy.setdefault(dest, 0)

    def _check_link(self, graph: Graph, src: str, dest: str,
                    link_usage: dict[str, dict[str, int]]) -> bool:
        """Tell whether a link still has room for one more drone.

        Args:
            graph: Zone network holding the link capacities.
            src: Zone the link starts from.
            dest: Zone the link goes to.
            link_usage: Per turn counter of the links already taken.

        Returns:
            True while the link is not saturated, False once as many
            drones as its capacity already took it this turn.
        """
        if link_usage[src][dest] >= self._max_link(graph, src, dest):
            return False
        return True

    def _check_hub(self, dest: str, graph: Graph,
                   occupancy: dict[str, int]) -> bool:
        """Tell whether a zone still has room for one more drone.

        The zone is added to ``occupancy`` first if it is not tracked
        yet, so the check never fails on a missing key.

        Args:
            dest: Zone a drone wants to enter.
            graph: Zone network holding the zone capacities.
            occupancy: Per turn counter of the drones on each zone.

        Returns:
            True while the zone is not saturated, False once it holds
            as many drones as its capacity.
        """
        if dest not in occupancy:
            self._init_occupancy(occupancy, dest)
        if occupancy[dest] >= graph.nodes[dest].max_drones:
            return False
        return True

    def _print_turn(self, moves: list[str]) -> None:
        """Print every move of the turn on a single line.

        Args:
            moves: Moves already formatted, ``D<id>-<zone>`` for a
                landing and ``D<id>-<src>-<dst>`` for a take off over
                a restricted zone.
        """
        print(" ".join(moves))

    def _drone_coord(self, graph: Graph,
                     drone: Drone) -> tuple[float, float]:
        """Give the position to draw a drone at, for the current turn.

        A drone in flight is not on a zone yet, since entering a
        restricted zone takes two turns, so it is placed halfway
        between the zone it left and the one it aims at. That is why
        the coordinates are floats and not the ints of the zones.

        Args:
            graph: Zone network holding the zone coordinates.
            drone: Drone to locate.

        Returns:
            The end zone coordinates if the drone is delivered, the
            middle of its current link if it is in flight, and the
            coordinates of the zone it sits on otherwise.
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
        """Snap the position and delivered flag of every drone.

        Args:
            graph: Zone network holding the zone coordinates.

        Returns:
            A :data:`Frame` of the fleet as it stands, ready to be
            appended to :attr:`history`.
        """
        frame: Frame = []
        for drone in self.drones:
            frame.append((drone.id, self._drone_coord(graph, drone),
                          drone.delivered))
        return frame

    def run(self, graph: Graph) -> int:
        """Move the whole fleet until every drone is delivered.

        Each turn the fleet is sorted by progress, the most advanced
        drones moving first so they free their zone for the ones
        behind. A drone then either lands on the next zone, takes off
        over a restricted zone, which costs it a second turn, or waits
        on its current zone when the link or the target zone is
        saturated. The moves are printed and a snapshot is appended to
        :attr:`history`, plus the initial one taken before the first
        turn.

        Args:
            graph: Zone network holding the capacities, the zone types
                and the end zone.

        Returns:
            The number of turns the delivery took.
        """
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
                       and self._check_hub(dest, graph, occupancy)
                       and graph.nodes[dest].zone_type != ZoneType.RESTRICTED):
                        drone.index += 1
                        link_usage[src][dest] += 1
                        if dest not in occupancy:
                            self._init_occupancy(occupancy, dest)
                        occupancy[dest] += 1
                        if dest == graph.get_end().name:
                            drone.delivered = True
                        moves.append(f"D{drone.id}-{dest}")
                    elif (self._check_link(graph, src, dest, link_usage)
                          and graph.nodes[dest].zone_type == ZoneType.
                          RESTRICTED):
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
