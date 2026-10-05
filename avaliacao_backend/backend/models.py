"""Recorte da avaliação: cidade (pai) e linha_onibus (dependente)."""
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Cidade(Base):
    __tablename__ = 'cidade'
    id_cidade: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    linhas: Mapped[list['LinhaOnibus']] = relationship(back_populates='cidade')

class LinhaOnibus(Base):
    __tablename__ = 'linha_onibus'
    __table_args__ = (UniqueConstraint('id_cidade', 'codigo', name='uq_linha_cidade_codigo'),)
    id_linha: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_cidade: Mapped[int] = mapped_column(ForeignKey('cidade.id_cidade'), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[Cidade] = relationship(back_populates='linhas')
