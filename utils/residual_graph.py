from utils import Graph
from copy import copy


class ResidualGraph:
    def __init__(self):
        self.residual: dict[str, dict[str, float]] = {}
        self.cap_init: dict[str, dict[str, float]] = {}
        self.start_path: str = ""
        self.end_path: str = ""

    def build_residual(self, graph: Graph) -> None:
        inf = float("inf")
        tmp_cap: float = 0.0
        for node in graph.nodes.values():
            if node.start:
                self.start_path = node.name+"_in"
            if node.end:
                self.end_path = node.name
            tmp_cap = inf if node.start or node.end else float(node.max_drones)
            self._add_arc(node+"_in", node+"_out", tmp_cap)

        for node in graph.nodes.keys():
            for edge in graph.edges[node]:
                self._add_arc(node+"_in", edge.dst+"_out",
                              float(edge.max_link))
        self.cap_init = copy(self.residual)

    def _add_arc(self, h_in: str, h_out: str, capacity: float) -> None:
        self.residual.setdefault(h_in, {})
        self.residual.setdefault(h_out, {})
        self.residual[h_in][h_out] = (self.residual[h_in].get(h_out, 0.0)
                                      + capacity)
        self.residual[h_out].setdefault(h_in, 0.0)

    def bfs(self, start_path: str, end_path: str) -> list[str] | None:
        checked: set[str] = {start_path}
        queue: list[str] = [start_path]
        previous: dict[str, str] = {}
        while queue:
            n = queue.pop(0)
            if n == end_path:
                return previous
            for next_n in self.residual[n].keys():
                if next_n not in checked and self.residual[n][next_n] > 0:
                    previous.setdefault(next_n, n)
                    queue.append(next_n)
        return None

    def maxflow(self, start_path: str, end_path: str) -> None:
        total_flow = 0
        while True:
            prev = self.bfs(start_path, end_path)
            total_flow += 1
            if prev is None:
                break
        pass
