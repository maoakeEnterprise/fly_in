import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from utils import ZoneType

from utils.graph import Graph, Node

Frame = list[tuple[int, tuple[float, float], bool]]


class Visualizer:
    def __init__(self, graph: Graph, history: list[Frame],
                 interval: int = 800) -> None:
        self.graph = graph
        self.history = history
        self.interval = interval
        self.paused = False

    def _draw_network(self, ax: Axes) -> None:
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
        print(f"node name: {node.name} zone : {node.zone_type.value}")
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
        for name, node in self.graph.complete_nodes.items():
            x, y = node.coord
            edgecolor, linewidth = self._border(node)
            ax.scatter(x, y, s=800, color=node.color, edgecolors=edgecolor,
                       linewidths=linewidth, zorder=2)
            ax.annotate(name, (x, y), xytext=(0, 20),
                        textcoords="offset points", ha="center", zorder=6)

    def _update(self, ax: Axes, idx: int, dynamic: list[Artist]
                ) -> list[Artist]:
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
        return dynamic

    def _legend(self) -> list[Line2D]:
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
        if event.key != " ":
            return
        if self.paused:
            self.anim.resume()
        else:
            self.anim.pause()
        self.paused = not self.paused

    def render(self) -> None:
        if not self.history:
            return
        dynamic: list[Artist] = []
        fig, ax = plt.subplots(figsize=(20, 20))
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
