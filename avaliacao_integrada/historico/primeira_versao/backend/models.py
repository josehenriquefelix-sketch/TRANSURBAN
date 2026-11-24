from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

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

    linhas = relationship(
        "LinhaOnibus",
        back_populates="cidade"
    )


class LinhaOnibus(Base):
    __tablename__ = "linha_onibus"
    __table_args__ = (
        UniqueConstraint("id_cidade", "codigo", name="uq_linha_cidade_codigo"),
    )

    id_linha = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String(120),
        nullable=False
    )

    codigo = Column(
        String(20),
        nullable=False
    )

    id_cidade = Column(
        Integer,
        ForeignKey("cidade.id_cidade"),
        nullable=False
    )

    cidade = relationship(
        "Cidade",
        back_populates="linhas"
    )
