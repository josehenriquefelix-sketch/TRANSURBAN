from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Cidade(Base):
    __tablename__ = "cidade"

    id_cidade: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False,
    )
    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
