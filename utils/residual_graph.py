from utils import Graph
from copy import deepcopy


class ResidualGraph:
    def __init__(self) -> None:
        self.residual: dict[str, dict[str, float]] = {}
        self.cap_init: dict[str, dict[str, float]] = {}
        self.start_path: str = ""
        self.end_path: str = ""

    def build_residual(self, graph: Graph) -> None:
        tmp_cap: float = 0.0
        for node in graph.nodes.values():
            if node.start:
                self.start_path = node.name + "_in"
            if node.end:
                self.end_path = node.name + "_out"
            tmp_cap = (graph.total_drones if node.start or node.end
                       else float(node.max_drones))
            self._add_arc(f"{node.name}_in", f"{node.name}_out", tmp_cap)

        for node in graph.nodes.keys():
            for edge in graph.edges[node]:
                self._add_arc(f"{node}_out", f"{edge.dst}_in",
                              float(edge.max_link))
        self.cap_init = deepcopy(self.residual)

    def _add_arc(self, h_in: str, h_out: str, capacity: float) -> None:
        self.residual.setdefault(h_in, {})
        self.residual.setdefault(h_out, {})
        self.residual[h_in][h_out] = (self.residual[h_in].get(h_out, 0.0)
                                      + capacity)
        self.residual[h_out].setdefault(h_in, 0.0)

    def bfs(self, start_path: str, end_path: str) -> dict[str, str] | None:
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

    def maxflow(self, start_path: str, end_path: str) -> float:
        total_flow = 0.0
        while True:
            prev = self.bfs(start_path, end_path)
            if prev is None:
                break
            tmp_f = float("inf")
            tmp_n = end_path
            while tmp_n != start_path:
                tmp_p = prev[tmp_n]
                tmp_f = min(tmp_f, self.residual[tmp_p][tmp_n])
                tmp_n = tmp_p
            tmp_n = end_path
            while tmp_n != start_path:
                tmp_p = prev[tmp_n]
                self.residual[tmp_p][tmp_n] -= tmp_f
                self.residual[tmp_n][tmp_p] += tmp_f
                tmp_n = tmp_p
            total_flow += tmp_f
        return total_flow

    def decompose(self, start: str, end: str) -> list[list[str]]:
        flow: dict[str, dict[str, float]] = {}
        for n in self.residual.keys():
            for next_n in self.residual[n].keys():
                tmp = self.cap_init[n][next_n] - self.residual[n][next_n]
                if tmp > 0:
                    flow.setdefault(n, {})
                    flow[n].setdefault(next_n, tmp)
        paths: list[list[str]] = []
        while flow.get(start) and any(f > 0 for f in flow[start].values()):
            node = start
            path: list[str] = [start]
            while node != end:
                next_n = next(tmp for tmp, f in flow[node].items() if f > 0)
                flow[node][next_n] -= 1
                path.append(next_n)
                node = next_n
            paths.append(path)
        return paths
