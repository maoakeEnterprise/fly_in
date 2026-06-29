from pydantic import BaseModel, Field, model_validator
from enum import Enum


class NameColor(Enum):
    RED = "red"
    YELLOW = "yellow"
    PURPLE = "purple"
    PINK = "pink"
    ORANGE = "orange"
    BLUE = "blue"


class Hub(BaseModel):
    type_hub: str
    name: str
    coord: tuple[int, int]
    color: str
    max_drones: int = Field(gt=0)
    zone: str
    nb_drones_in: int

    @model_validator(mode="after")
    def check_hub(self) -> 'Hub':
        if self.color not in NameColor:
            self.color = NameColor.YELLOW.value
        if self.type_hub in ["start_hub", "end_hub"]:
            if self.zone != "normal":
                raise ValueError(f"{self.type_hub} should be a normal zone")
        return self
