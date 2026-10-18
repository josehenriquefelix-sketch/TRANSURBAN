"""Tabelas, chaves e restrições de integridade."""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint, CheckConstraint
from database import Base

class Cidade(Base):
    __tablename__ = 'cidade'
    id_cidade = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)

class Linha(Base):
    __tablename__ = 'linha_onibus'
    id_linha = Column(Integer, primary_key=True)
    id_cidade = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(120), nullable=False)
    __table_args__ = (UniqueConstraint('id_cidade', 'codigo'),)

class Trecho(Base):
    __tablename__ = 'trecho'
    id_trecho = Column(Integer, primary_key=True)
    id_cidade_origem = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    id_cidade_destino = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    nome = Column(String(150), nullable=False)
    distancia_km = Column(Float, nullable=False)
    __table_args__ = (CheckConstraint('distancia_km > 0'), CheckConstraint('id_cidade_origem <> id_cidade_destino'))

class Percurso(Base):
    __tablename__ = 'linha_trecho'
    id_linha = Column(Integer, ForeignKey('linha_onibus.id_linha'), primary_key=True)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), primary_key=True)
    ordem = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('id_linha', 'ordem'), CheckConstraint('ordem > 0'))

class Faixa(Base):
    __tablename__ = 'faixa_exclusiva'
    id_faixa = Column(Integer, primary_key=True)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), nullable=False)
    tipo = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    __table_args__ = (CheckConstraint("tipo IN ('EXCLUSIVA','PREFERENCIAL')"), CheckConstraint("status IN ('ATIVA','INATIVA','PLANEJADA')"))

class Atraso(Base):
    __tablename__ = 'registro_atraso'
    id_atraso = Column(Integer, primary_key=True)
    id_linha = Column(Integer, ForeignKey('linha_onibus.id_linha'), nullable=False)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), nullable=False)
    data_registro = Column(Date, nullable=False)
    minutos_atraso = Column(Integer, nullable=False)
    observacao = Column(String(255), nullable=False, default='')
    __table_args__ = (CheckConstraint('minutos_atraso >= 0'),)

