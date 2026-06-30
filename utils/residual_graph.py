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
            self._add_arc(f"{node}_in", f"{node}_out", tmp_cap)

        for node in graph.nodes.keys():
            for edge in graph.edges[node]:
                self._add_arc(f"{node}_in", f"{edge.dst}_out",
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
            for next_n, cap in self.residual[n].items():
                if next_n not in checked and cap > 0:
                    previous.setdefault(next_n, n)
                    checked.add(next_n)
                    queue.append(next_n)
        return None

    def maxflow(self, start_path: str, end_path: str) -> None:
        total_flow = 0.0
        while True:
            prev = self.bfs(start_path, end_path)
            total_flow += 1
            if prev is None:
                break
            tmp_f = float("inf")
            tmp_n = end_path
            while tmp_n != start_path:
                tmp_p = prev[tmp_n]
                tmp_f = min(tmp_f, self.residual[tmp_n][tmp_f])
                tmp_n = tmp_p
            tmp_n = end_path
            while tmp_n != start_path:
                tmp_p = prev[tmp_n]
                self.residual[tmp_p][tmp_n] -= tmp_f
                self.residual[tmp_n][tmp_p] == tmp_f
            total_flow += tmp_f
        return total_flow
