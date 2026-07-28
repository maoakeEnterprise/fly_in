from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from utils.graph import Graph, Node

Frame = list[tuple[int, tuple[float, float], bool]]


class Visualizer:
    def __init__(self, graph: Graph, history: list[Frame],
                 interval: int = 800) -> None:
        self.graph = graph
        self.history = history
        self.interval = interval

    def render(self) -> None:
        fig, ax = plt.subplots(figsize=(20, 20))
        ax.axis("off")
        self._draw_network(ax)
        self._draw_hub(ax)
        plt.show()

    def _draw_network(self, ax: Axes) -> None:
        drawn = set()
        for name, edges in self.graph.edges.items():
            if name not in self.graph.nodes:
                continue
            x0, y0 = self.graph.nodes[name].coord
            for edge in edges:
                key = frozenset((name, edge.dst))
                if key in drawn:
                    continue
                x1, y1 = self.graph.nodes[edge.dst].coord
                ax.plot([x0, x1], [y0, y1], color="black", lw=1.4, zorder=1)

    def _border(self, node: Node) -> tuple[str, float]:
        if node.start:
            return ("green", 2.4)
        if node.end:
            return ("red", 2.4)
        return ("black", 1.1)

    def _draw_hub(self, ax: Axes) -> None:
        for name, node in self.graph.nodes.items():
            x, y = node.coord
            edgecolor, linewidth = self._border(node)
            ax.scatter(x, y, s=800, color=node.color, edgecolors=edgecolor,
                       linewidths=linewidth, zorder=2)
            ax.annotate(name, (x, y), xytext=(0, 20),
                        textcoords="offset points", ha="center", zorder=6)

    def _update(self, ax: Axes, idx: int, dynamic: list[Artist]) -> None:
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
                         f"Delivered: {delivered / total}")
        return dynamic
