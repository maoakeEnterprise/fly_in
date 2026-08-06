"""Unit moved by the Fly-in simulator.

Holds one drone and the route it was assigned when the fleet was
spread over the paths. The drone owns no logic of its own: the
simulator advances its index turn after turn and flips its flags, so
this module is only the state carried between two turns.
"""


class Drone:
    """
    we give id for the drone to identify him
    the path he will follow already calculate
    we need index to know where he is in the path
    delivered to know if he is in the end or not
    in flight to know if he is on a link
    Attributes:
        id: id on a drone
        path: the path he will travel
        index: to know where he is in the path
        delivered: to know if he finished the travel
        in_flight: to know if he is on a connection
    """
    def __init__(self, id: int, path: list[str]):
        """Create a drone"""
        self.id = id
        self.path = path
        self.index = 0
        self.delivered = False
        self.in_flight = False
