"""Tabelas do site de demonstração; separadas das entidades da avaliação DS."""
from sqlalchemy import Boolean, Column, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, text
from database import Base

class ContaWeb(Base):
    __tablename__='web_conta'
    id=Column(String(36),primary_key=True)
    nome=Column(String(80),nullable=False)
    email=Column(String(160),nullable=False,unique=True)
    senha_hash=Column(String(250),nullable=False)
    perfil=Column(String(20),nullable=False)
    criada_em=Column(Integer,nullable=False)

class SessaoWeb(Base):
    __tablename__='web_sessao'
    token_hash=Column(String(64),primary_key=True)
    conta_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False,index=True)
    expira_em=Column(Integer,nullable=False)

class PercursoWeb(Base):
    __tablename__='web_percurso'
    id=Column(String(36),primary_key=True)
    conta_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False,index=True)
    pontos=Column(JSON,nullable=False)
    geometria=Column(JSON,nullable=True)
    instrucoes=Column(JSON,nullable=False,default=list)
    distancia_m=Column(Float,nullable=True)
    fonte=Column(String(200),nullable=False)
    criado_em=Column(Integer,nullable=False)

class ViagemWeb(Base):
    __tablename__='web_viagem'
    id=Column(String(36),primary_key=True)
    motorista_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False,index=True)
    linha_id=Column(String(100),nullable=False)
    veiculo=Column(String(20),nullable=False)
    sentido=Column(String(100),nullable=False)
    percurso_id=Column(String(36),ForeignKey('web_percurso.id'),nullable=True)
    ativa=Column(Boolean,nullable=False,default=True)
    iniciada_em=Column(Integer,nullable=False)
    encerrada_em=Column(Integer,nullable=True)
    latitude=Column(Float,nullable=True)
    longitude=Column(Float,nullable=True)
    precisao_m=Column(Float,nullable=True)
    velocidade_m_s=Column(Float,nullable=True)
    gps_em=Column(Integer,nullable=True)
    lotacao_motorista=Column(String(20),nullable=True)
    lotacao_em=Column(Integer,nullable=True)

Index('web_uma_viagem_ativa_por_motorista',ViagemWeb.motorista_id,unique=True,
      sqlite_where=text('ativa = 1'),postgresql_where=text('ativa = true'))

class EmbarqueWeb(Base):
    __tablename__='web_embarque'
    id=Column(String(36),primary_key=True)
    passageiro_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False,index=True)
    viagem_id=Column(String(36),ForeignKey('web_viagem.id'),nullable=False,index=True)
    ponto_embarque=Column(Integer,nullable=True)
    ponto_desembarque=Column(Integer,nullable=True)
    ativo=Column(Boolean,nullable=False,default=True)
    criado_em=Column(Integer,nullable=False)
    encerrado_em=Column(Integer,nullable=True)

Index('web_um_embarque_ativo_por_passageiro',EmbarqueWeb.passageiro_id,unique=True,
      sqlite_where=text('ativo = 1'),postgresql_where=text('ativo = true'))

class AvaliacaoWeb(Base):
    __tablename__='web_avaliacao'
    id=Column(String(36),primary_key=True)
    embarque_id=Column(String(36),ForeignKey('web_embarque.id'),nullable=False,unique=True)
    passageiro_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False)
    viagem_id=Column(String(36),ForeignKey('web_viagem.id'),nullable=False,index=True)
    nota=Column(Integer,nullable=False)
    descricao=Column(Text,nullable=False)
    lotacao=Column(String(20),nullable=False)
    criada_em=Column(Integer,nullable=False)

class RelatoLotacaoWeb(Base):
    __tablename__='web_lotacao'
    id=Column(String(36),primary_key=True)
    embarque_id=Column(String(36),ForeignKey('web_embarque.id'),nullable=False,unique=True)
    viagem_id=Column(String(36),ForeignKey('web_viagem.id'),nullable=False,index=True)
    lotacao=Column(String(20),nullable=False)
    atualizado_em=Column(Integer,nullable=False)

class LancamentoWeb(Base):
    __tablename__='web_lancamento'
    __table_args__=(UniqueConstraint('conta_id','chave_idempotencia',name='web_lancamento_idempotente'),)
    id=Column(String(36),primary_key=True)
    conta_id=Column(String(36),ForeignKey('web_conta.id'),nullable=False,index=True)
    tipo=Column(String(25),nullable=False)
    valor_centavos=Column(Integer,nullable=False)
    metodo=Column(String(20),nullable=False)
    parcelas=Column(Integer,nullable=False)
    origem=Column(String(100),nullable=True)
    chave_idempotencia=Column(String(80),nullable=False)
    criado_em=Column(Integer,nullable=False)
