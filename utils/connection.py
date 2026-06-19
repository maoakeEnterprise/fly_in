from pydantic import BaseModel, Field
from utils.hub import Hub


class Connection(BaseModel):
    hub1: Hub
    hub2: Hub
    max_link: int = Field(gt=0)
