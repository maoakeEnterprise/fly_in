from utils import Drone
from utils import Graph


class Simulator:
    def __init__(self):
        self.drones: list[Drone] = []

    def load_drones(self, paths: list[list[str]], count_d: list[int]) -> None:
        id = 0
        j = 0
        for i in count_d:
            for _ in range(i):
                self.drones.append(Drone(id, paths[j]))
                id += 1
            j += 1

    def is_every_drones_delivered(self) -> bool:
        for drone in self.drones:
            if drone.delivered is False:
                return False
        return True

    def run(self, graph: Graph) -> None:
        while self.is_every_drones_delivered() is False:
            # moves: list[str] = []
            # occupancy: dict[str, int] = {}
            # link_usage: dict[str, int] = {}
            for drone in self.drones:
                if drone.delivered:
                    continue
