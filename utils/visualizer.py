from __future__ import annotations

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from utils.graph import Graph, Node

Frame = list[tuple[int, tuple[float, float], bool]]


class Visualizer:
    """Animated matplotlib representation of a drone simulation.

    The network of zones is drawn once as a static background: each zone
    is filled with the color given in the map file, falling back to a
    default color when that value is not a renderable color. Start and
    end zones keep a distinctive colored border so they stay easy to
    spot whatever their fill color is. A dynamic layer is then animated
    turn by turn from the positional history recorded by the simulator,
    showing how many drones occupy each zone or connection every turn.
    """

    DEFAULT_COLOR = "#cccccc"
    START_EDGE = "#1e8449"
    END_EDGE = "#922b21"
    CLOSE_DELAY_MS = 3000

    def __init__(self, graph: Graph, history: list[Frame],
                 interval: int = 800) -> None:
        self.graph = graph
        self.history = history
        self.interval = interval
        self.total = len(history[0]) if history else 0

    def _node_color(self, node: Node) -> str:
        """Return the fill color given in the map, or the default.

        The default color is used when the map provides no usable value
        (``none``) or a name matplotlib cannot render.
        """
        color = node.color
        if (color and color.lower() != "none"
                and mcolors.is_color_like(color)):
            return color
        return self.DEFAULT_COLOR

    def _border(self, node: Node) -> tuple[str, float]:
        """Return the (color, width) of a zone border, by role."""
        if node.start:
            return (self.START_EDGE, 2.4)
        if node.end:
            return (self.END_EDGE, 2.4)
        return ("black", 1.1)

    def _draw_network(self, ax: Axes) -> None:
        """Draw the static background: connections then zones."""
        drawn: set[frozenset[str]] = set()
        for name, edges in self.graph.edges.items():
            if name not in self.graph.nodes:
                continue
            x0, y0 = self.graph.nodes[name].coord
            for edge in edges:
                if edge.dst not in self.graph.nodes:
                    continue
                key = frozenset((name, edge.dst))
                if key in drawn:
                    continue
                drawn.add(key)
                x1, y1 = self.graph.nodes[edge.dst].coord
                ax.plot([x0, x1], [y0, y1], color="#ccd1d9",
                        lw=1.4, zorder=1)
        for name, node in self.graph.nodes.items():
            x, y = node.coord
            edge_color, edge_width = self._border(node)
            ax.scatter(x, y, s=680, color=self._node_color(node),
                       edgecolors=edge_color, linewidths=edge_width,
                       zorder=2)
            ax.annotate(name, (x, y), xytext=(0, 14),
                        textcoords="offset points", fontsize=6.5,
                        ha="center", va="bottom", zorder=6)

    def _legend_handles(self) -> list[Line2D]:
        """Build legend entries: start/end borders and the default fill."""
        return [
            Line2D([0], [0], marker="o", color="white", label="start",
                   markerfacecolor="white", markeredgecolor=self.START_EDGE,
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white", label="end",
                   markerfacecolor="white", markeredgecolor=self.END_EDGE,
                   markeredgewidth=2.4, markersize=11),
            Line2D([0], [0], marker="o", color="white",
                   label="unknown color → default",
                   markerfacecolor=self.DEFAULT_COLOR,
                   markeredgecolor="black", markersize=11),
        ]

    def _update(self, ax: Axes, dynamic: list[Artist],
                idx: int) -> list[Artist]:
        """Redraw the drone layer for turn ``idx``."""
        for art in dynamic:
            art.remove()
        dynamic.clear()
        counts: dict[tuple[float, float], int] = {}
        for _, coord, _ in self.history[idx]:
            counts[coord] = counts.get(coord, 0) + 1
        for (x, y), nb in counts.items():
            marker = ax.scatter(x, y, s=300, color="#111111",
                                edgecolors="white", linewidths=1.0,
                                zorder=4)
            label = ax.annotate(str(nb), (x, y), color="white",
                                fontsize=8, ha="center", va="center",
                                fontweight="bold", zorder=5)
            dynamic.extend([marker, label])
        delivered = sum(1 for _, _, done in self.history[idx] if done)
        ax.set_title(f"Turn {idx}/{len(self.history) - 1}      "
                     f"delivered: {delivered}/{self.total}",
                     fontsize=13, fontweight="bold")
        return dynamic

    def render(self, save_path: str | None = None) -> None:
        """Play the animation, or save it when ``save_path`` is given.

        A ``.gif`` path uses the Pillow writer, any other extension uses
        the ffmpeg writer. Without a path the animation is shown in an
        interactive window.
        """
        if not self.history:
            return
        if save_path:
            matplotlib.use("Agg")
        fig, ax = plt.subplots(figsize=(13, 8))
        self._draw_network(ax)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.legend(handles=self._legend_handles(), loc="lower center",
                   ncol=3, fontsize=9, framealpha=0.9)
        dynamic: list[Artist] = []
        anim = FuncAnimation(
            fig, lambda idx: self._update(ax, dynamic, idx),
            frames=len(self.history), interval=self.interval,
            blit=False, repeat=False)
        fps = max(1, round(1000 / self.interval))
        if save_path and save_path.endswith(".gif"):
            anim.save(save_path, writer=PillowWriter(fps=fps))
            plt.close(fig)
        elif save_path:
            anim.save(save_path, writer=FFMpegWriter(fps=fps))
            plt.close(fig)
        else:
            delay = len(self.history) * self.interval + self.CLOSE_DELAY_MS
            timer = fig.canvas.new_timer(interval=delay)
            timer.single_shot = True
            timer.add_callback(lambda: plt.close(fig))
            timer.start()
            plt.show()
