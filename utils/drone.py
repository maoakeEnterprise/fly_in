class Drone:
    """we give id for the drone to identify him
       the path he will follow already calculate
       we need index to know where he is in the path
       delivered to know if he is in the end or not
       in flight to know if he is on a link
    """
    def __init__(self, id: int, path: list[str]):
        self.id = id
        self.path = path
        self.index = 0
        self.delivered = False
        self.in_flight = False
