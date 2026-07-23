from pydantic import BaseModel, Field, model_validator


class Hub(BaseModel):
    """A parsed zone carrying its raw metadata.

    The ``color`` given in the map file is kept verbatim; validating
    whether it is a renderable color is left to the visual layer.
    """

    type_hub: str
    name: str
    coord: tuple[int, int]
    color: str
    max_drones: int = Field(gt=0)
    zone: str
    nb_drones_in: int

    @model_validator(mode="after")
    def check_hub(self) -> 'Hub':
        """Ensure start and end zones keep a normal movement cost."""
        if self.type_hub in ["start_hub", "end_hub"]:
            if self.zone != "normal":
                raise ValueError(f"{self.type_hub} should be a normal zone")
        return self
