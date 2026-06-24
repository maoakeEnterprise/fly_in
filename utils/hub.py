from pydantic import BaseModel, Field


class Hub(BaseModel):
    type_hub: str
    name: str
    coord: tuple[int, int]
    color: str
    max_drones: int = Field(gt=0)
    zone: str
    nb_drones_in: int
