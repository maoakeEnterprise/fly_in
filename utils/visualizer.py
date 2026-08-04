"""Animated replay of a Fly-in simulation.

Draws the map once with matplotlib, then walks the history recorded by
:mod:`utils.simulator` turn by turn, moving the fleet over the fixed
background. The window closes on its own shortly after the last turn.
"""
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from utils import ZoneType

from utils.graph import Graph, Node

Frame = list[tuple[int, tuple[float, float], bool]]
"""State of the whole fleet at one turn.

Mirrors the alias of :mod:`utils.simulator`: one tuple per drone,
holding its id, its position as floats and whether it is delivered.
"""


class Visualizer:
    """Animation window replaying a finished simulation.

    The map is drawn once and never redrawn; only the drone markers
    are cleared and rebuilt at each turn, which is why the animation
    runs without blitting.

    Attributes:
        graph: Zone network to draw, read through its ``complete_``
            collections so blocked zones stay visible.
        history: Turns to replay, as recorded by the simulator.
        interval: Milliseconds a turn stays on screen, reused as the
            delay before the window closes.
        paused: Whether the animation is currently on hold.
        closed: Whether the closing timer was already armed, so the
            last turn cannot arm it twice.
        fig: Figure holding the drawing, set by :meth:`render`.
        anim: Running animation, set by :meth:`render`.
        timer: One-shot timer closing the window, set by
            :meth:`_shedule_close`.
    """

    def __init__(self, graph: Graph, history: list[Frame],
                 interval: int = 800) -> None:
        """Prepare a replay, without drawing anything yet.

        Args:
            graph: Zone network to draw.
            history: Turns to replay, the first entry being the fleet
                before any move.
            interval: Milliseconds a turn stays on screen.
        """
        self.graph = graph
        self.history = history
        self.interval = interval
        self.paused = False
        self.closed = False

    def _draw_network(self, ax: Axes) -> None:
        """Draw every connection of the map as a black segment.

        Links being stored in both directions, each pair of zones is
        remembered once drawn so the segment is not drawn twice.

        Args:
            ax: Axes to draw on.
        """
        drawn = set()
        for name, edges in self.graph.complete_edges.items():
            if name not in self.graph.complete_nodes:
                continue
            x0, y0 = self.graph.complete_nodes[name].coord
            for edge in edges:
                key = frozenset((name, edge.dst))
                if key in drawn:
                    continue
                drawn.add(key)
                x1, y1 = self.graph.complete_nodes[edge.dst].coord
                ax.plot([x0, x1], [y0, y1], color="black", lw=1.4, zorder=1)

    def _border(self, node: Node) -> tuple[str, float]:
        """Give the outline telling what kind of zone this is.

        The zone color itself comes from the map file, so the role of
        the zone is carried by its border instead. Being the start or
        the end wins over the zone type, which the models guarantee is
        normal there anyway.

        Args:
            node: Zone about to be drawn.

        Returns:
            A ``(color, width)`` pair: green for the start, red for
            the end, purple for a restricted zone, a thick gray for a
            blocked one, and a thin black for any other.
        """
        if node.start:
            return ("green", 2.4)
        if node.end:
            return ("red", 2.4)
        if node.zone_type == ZoneType.RESTRICTED:
            return ("purple", 2.4)
        if node.zone_type == ZoneType.BLOCKED:
            return ("gray", 4.4)
        return ("black", 1.1)

    def _draw_hub(self, ax: Axes) -> None:
        """Draw every zone as a filled dot carrying its name.

        Args:
            ax: Axes to draw on.
        """
        for name, node in self.graph.complete_nodes.items():
            x, y = node.coord
            edgecolor, linewidth = self._border(node)
            ax.scatter(x, y, s=800, color=node.color, edgecolors=edgecolor,
                       linewidths=linewidth, zorder=2)
            ax.annotate(name, (x, y), xytext=(0, 20),
                        textcoords="offset points", ha="center", zorder=6)

    def _update(self, ax: Axes, idx: int, dynamic: list[Artist]
                ) -> list[Artist]:
        """Redraw the fleet for one turn of the history.

        Drones sharing a position are drawn as a single marker
        carrying how many they are, which keeps a crowded zone
        readable and shows the capacities at work. The markers of the
        previous turn are removed first, the map underneath being left
        untouched.

        Args:
            ax: Axes to draw on.
            idx: Turn to draw, an index into ``history``.
            dynamic: Markers of the previous turn, emptied and refilled
                in place.

        Returns:
            ``dynamic``, now holding the markers of this turn, as
            :class:`~matplotlib.animation.FuncAnimation` expects.
        """
        counts: dict[tuple[float, float], int] = {}
        for art in dynamic:
            art.remove()
        dynamic.clear()
        for _, coord, _ in self.history[idx]:
            if coord in counts:
                counts[coord] += 1
            else:
                counts.setdefault(coord, 1)
        for (x, y), nb in counts.items():
            drone_pos = ax.scatter(x, y, s=300, color="#111111",
                                   edgecolors="white", linewidths=1.0,
                                   zorder=4)
            label = ax.annotate(str(nb), (x, y), color="white", fontsize=8,
                                ha="center", va="center", fontweight="bold",
                                zorder=5)
            dynamic.extend([drone_pos, label])
            delivered = sum(1 for _, _, dv in self.history[idx] if dv)
            total = len(self.history[idx])
            ax.set_title(f"Turn {idx} / {len(self.history) - 1}  "
                         f"Delivered: {delivered} / {total}")
            if idx == (len(self.history) - 1):
                self._shedule_close()
        return dynamic

    def _legend(self) -> list[Line2D]:
        """Build the legend explaining the outlines used on the map.

        Returns:
            One dummy marker per border meaning of :meth:`_border`,
            plus one for a zone whose color the map file got wrong and
            which the graph fell back to gray.
        """
        return [
            Line2D([0], [0], marker="o", color="white", label="start",
                   markerfacecolor="white", markeredgecolor="green",
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white", label="end",
                   markerfacecolor="white", markeredgecolor="red",
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white", label="restricted",
                   markerfacecolor="white", markeredgecolor="purple",
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white", label="blocked",
                   markerfacecolor="white", markeredgecolor="gray",
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white",
                   label="unknown color → default",
                   markerfacecolor="gray",
                   markeredgecolor="black", markersize=11),
        ]

    def _on_key(self, event: KeyEvent) -> None:
        """Pause or resume the replay when space is pressed.

        Any other key is ignored. Useful to stop on a turn and read
        the fleet, since a busy map goes by fast.

        Args:
            event: Key press reported by the matplotlib canvas.
        """
        if event.key != " ":
            return
        if self.paused:
            self.anim.resume()
        else:
            self.anim.pause()
        self.paused = not self.paused

    def _shedule_close(self) -> None:
        """Arm a one-shot timer closing the window.

        Waits one interval before closing, so the last turn stays on
        screen as long as the others instead of flashing by. Called
        from every marker of the last turn, hence the ``closed`` guard
        making the timer be armed only once.
        """
        if self.closed:
            return
        self.closed = True
        self.timer = self.fig.canvas.new_timer(
            interval=self.interval
        )
        self.timer.single_shot = True
        self.timer.add_callback(lambda: plt.close(self.fig))
        self.timer.start()

    def render(self) -> None:
        """Draw the map, then run the replay until the window closes.

        Blocks on :func:`~matplotlib.pyplot.show` until the closing
        timer fires or the user closes the window. Does nothing at all
        when the history is empty.
        """
        if not self.history:
            return
        dynamic: list[Artist] = []
        fig, ax = plt.subplots(figsize=(20, 20))
        self.fig = fig
        ax.axis("off")
        self._draw_network(ax)
        self._draw_hub(ax)
        fig.legend(
            handles=self._legend(), loc="lower center",
            ncol=5, fontsize=9
        )
        self.anim = FuncAnimation(
            fig,
            lambda idx: self._update(ax, idx, dynamic),
            frames=len(self.history),
            interval=self.interval,
            blit=False,
            repeat=False,
        )
        fig.canvas.mpl_connect("key_press_event", self._on_key)
        plt.show()
