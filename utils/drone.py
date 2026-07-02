class Drone:
    def __init__(self, id: int, path: list[str]):
        self.id = id
        self.path = path
        self.index = 0
        self.delivered = False
        self.in_flight = False
