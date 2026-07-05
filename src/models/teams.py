from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

if TYPE_CHECKING:
    from src.models.players import Player

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tag: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    captain_id: Mapped[int] = mapped_column(
        ForeignKey('players.id', ondelete="SET NULL"), nullable=False
    )
    players: Mapped[list["Player"]] = relationship(
        back_populates="team",
        foreign_keys="Player.team_id"
    )