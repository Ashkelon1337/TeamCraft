from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
import enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.teams import Team

class GameRole(str, enum.Enum):
    IGL = "igl"
    AWPER = "awper"
    ENTRY = "entry"
    SUPPORT = "support"
    LURKER = "lurker"
    NONE = "none"

class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    USER = 'user'

class Player(Base):
    __tablename__ = 'players'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), default=UserRole.USER, nullable=False)
    game_role: Mapped[GameRole] = mapped_column(String(20), default=GameRole.NONE, nullable=False)
    game_rank: Mapped[int] = mapped_column(Integer, default=0)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    team: Mapped[Optional["Team"]] = relationship(back_populates='players', foreign_keys=[team_id])
    