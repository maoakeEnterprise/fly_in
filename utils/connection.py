from pydantic import BaseModel, Field


class Connection(BaseModel):
    name_hub1: str
    name_hub2: str
    max_link: int = Field(gt=0)
    nb_drones_in: int = 0
