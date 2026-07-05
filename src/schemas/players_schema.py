from pydantic import BaseModel
from typing import Optional

class PlayerResponse(BaseModel):
    id: int
    username: str
    game_role: str
    game_rank: int
    team_id: Optional[int]
    role: str

