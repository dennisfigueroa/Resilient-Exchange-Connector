from pydantic import BaseModel
from typing import List, Tuple


class Spread(BaseModel):
    symbol: str
    spread: float
    exchanges: Tuple[str, str]
    ts: int


class Health(BaseModel):
    status: str
