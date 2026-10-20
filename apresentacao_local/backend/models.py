from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Cidade(Base):
    __tablename__ = "cidade"
    id_cidade = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    linhas = relationship("LinhaOnibus", back_populates="cidade")

class LinhaOnibus(Base):
    __tablename__ = "linha_onibus"
    id_linha = Column(Integer, primary_key=True, index=True)
    id_cidade = Column(Integer, ForeignKey("cidade.id_cidade"), nullable=False, index=True)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(150), nullable=False)
    cidade = relationship("Cidade", back_populates="linhas")
