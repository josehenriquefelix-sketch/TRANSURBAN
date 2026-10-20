from sqlalchemy import Column, Integer, String

from database import Base


class Cidade(Base):
    __tablename__ = "cidade"

    id_cidade = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String(100),
        nullable=False,
        unique=True
    )
