"""A parsed link between two zones.

Mirrors a connection line of the map file, before the graph turns it
into the oriented edges the pathfinding walks through. The capacity is
validated here, while the existence of both zones is checked later by
the graph.
"""
from pydantic import BaseModel, Field


class Connection(BaseModel):
    """
    BaseModel for the connection
    Attributes:
        name_hub1: first hub
        name_hub2: second hub to make a connection
        max_link: nb drones who can be at the same time
        nb_drones_in: nb droness who are on this link
    """
    name_hub1: str
    name_hub2: str
    max_link: int = Field(gt=0)
    nb_drones_in: int = 0
