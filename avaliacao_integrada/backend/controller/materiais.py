"""CRUD e fechamento transacional de fornecimento de materiais da frota."""
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from postgrest.exceptions import APIError
from backend.auth import administrador
from backend.database import get_supabase

router=APIRouter(prefix='/gestao/estoque',tags=['Gestão · Materiais e itens'],dependencies=[Depends(administrador)])
Id=Annotated[int,Path(gt=0)]
Dinheiro=Annotated[Decimal,Field(ge=0,max_digits=12,decimal_places=2)]

@router.get('/esquema')
def estrutura_banco():
    from backend.esquema import consultar
    return consultar()

class Entrada(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)

class Unidade(Entrada):
    nome:str=Field(min_length=2,max_length=100)
    limite:Dinheiro

class Material(Entrada):
    nome:str=Field(min_length=2,max_length=100)
    categoria:Literal['pecas','limpeza','acessibilidade','seguranca','outros']
    valor_unitario:Annotated[Decimal,Field(gt=0,max_digits=12,decimal_places=2)]
    estoque:int=Field(ge=0,le=2147483647)

class Quantidade(Entrada):
    quantidade:int=Field(gt=0,le=2147483647)

class Item(Quantidade):
    material_id:int=Field(gt=0)

class OrdemBase(Entrada):
    unidade_id:int=Field(gt=0)
    data_ordem:date
    prefixo:str=Field(default='',max_length=30)

class Ordem(OrdemBase):
    itens:list[Item]=Field(min_length=1,max_length=100)

    @model_validator(mode='after')
    def sem_repetidos(self):
        if len({i.material_id for i in self.itens})!=len(self.itens):
            raise ValueError('Inclua cada material uma vez e informe sua quantidade.')
        return self

class Pagamento(Entrada):
    forma_pagamento:Literal['dinheiro','pix','cartao','fiado']

def executar(consulta):
    try:return consulta(get_supabase()).execute().data
    except APIError as erro:
        if erro.code in {'P0002'}:raise HTTPException(404,str(erro.message)) from erro
        if erro.code in {'P0001','23505','23503','23514'}:raise HTTPException(409,str(erro.message) if erro.code=='P0001' else 'Registro vinculado ou regra de integridade não atendida.') from erro
        if erro.code in {'42P01','PGRST205','PGRST202'}:raise HTTPException(503,'Aplique o script 09_materiais_e_ordens.sql no banco antes de usar esta área.') from erro
        raise

def um(tabela,id):
    registros=executar(lambda db:db.table(tabela).select('*').eq('id',id).limit(1))
    if not registros:raise HTTPException(404,'Registro não encontrado.')
    return registros[0]

def atualizar(tabela,id,dados):
    registros=executar(lambda db:db.table(tabela).update(dados.model_dump(mode='json')).eq('id',id))
    if not registros:raise HTTPException(404,'Registro não encontrado.')
    return registros[0]

def excluir(tabela,id):
    registros=executar(lambda db:db.table(tabela).delete().eq('id',id))
    if not registros:raise HTTPException(404,'Registro não encontrado.')
    return Response(status_code=204)

@router.get('/unidades')
def unidades():return executar(lambda db:db.table('tu_unidade').select('*').order('nome'))
@router.post('/unidades',status_code=201)
def criar_unidade(dados:Unidade):return executar(lambda db:db.table('tu_unidade').insert(dados.model_dump(mode='json')))[0]
@router.get('/unidades/{id}')
def unidade(id:Id):return um('tu_unidade',id)
@router.put('/unidades/{id}')
def editar_unidade(id:Id,dados:Unidade):return atualizar('tu_unidade',id,dados)
@router.delete('/unidades/{id}',status_code=204)
def apagar_unidade(id:Id):return excluir('tu_unidade',id)

@router.get('/materiais')
def materiais():return executar(lambda db:db.table('tu_material').select('*').order('nome'))
@router.post('/materiais',status_code=201)
def criar_material(dados:Material):return executar(lambda db:db.table('tu_material').insert(dados.model_dump(mode='json')))[0]
@router.get('/materiais/{id}')
def material(id:Id):return um('tu_material',id)
@router.put('/materiais/{id}')
def editar_material(id:Id,dados:Material):return atualizar('tu_material',id,dados)
@router.delete('/materiais/{id}',status_code=204)
def apagar_material(id:Id):return excluir('tu_material',id)

@router.get('/ordens')
def ordens():return executar(lambda db:db.table('tu_ordem_material').select('*,unidade:tu_unidade(nome)').order('id',desc=True))
@router.post('/ordens',status_code=201)
def abrir_ordem(dados:Ordem,usuario=Depends(administrador)):
    return executar(lambda db:db.rpc('tu_abrir_ordem_material',{'p_unidade':dados.unidade_id,'p_data':str(dados.data_ordem),'p_prefixo':dados.prefixo,'p_itens':[i.model_dump() for i in dados.itens],'p_autor':usuario['id']}))
@router.get('/ordens/{id}')
def ordem(id:Id):return um('tu_ordem_material',id)
@router.put('/ordens/{id}')
def editar_ordem(id:Id,dados:OrdemBase):
    return executar(lambda db:db.rpc('tu_alterar_ordem_material',{'p_ordem':id,'p_unidade':dados.unidade_id,'p_data':str(dados.data_ordem),'p_prefixo':dados.prefixo,'p_excluir':False}))
@router.delete('/ordens/{id}',status_code=204)
def apagar_ordem(id:Id):
    executar(lambda db:db.rpc('tu_alterar_ordem_material',{'p_ordem':id,'p_unidade':None,'p_data':None,'p_prefixo':None,'p_excluir':True}))
    return Response(status_code=204)
@router.post('/ordens/{id}/finalizar')
def finalizar(id:Id,dados:Pagamento):return executar(lambda db:db.rpc('tu_finalizar_ordem_material',{'p_ordem':id,'p_pagamento':dados.forma_pagamento}))

@router.get('/ordens/{id}/itens')
def itens(id:Id):
    um('tu_ordem_material',id)
    return executar(lambda db:db.table('tu_item_material').select('*,material:tu_material(nome)').eq('ordem_id',id).order('material_id'))
@router.get('/ordens/{id}/itens/{material_id}')
def item(id:Id,material_id:Id):
    registros=executar(lambda db:db.table('tu_item_material').select('*').eq('ordem_id',id).eq('material_id',material_id))
    if not registros:raise HTTPException(404,'Item não encontrado pelo par ordem/material.')
    return registros[0]
@router.post('/ordens/{id}/itens',status_code=201)
def incluir_item(id:Id,dados:Item):return executar(lambda db:db.rpc('tu_editar_item_material',{'p_ordem':id,'p_material':dados.material_id,'p_quantidade':dados.quantidade,'p_acao':'incluir'}))
@router.put('/ordens/{id}/itens/{material_id}')
def editar_item(id:Id,material_id:Id,dados:Quantidade):return executar(lambda db:db.rpc('tu_editar_item_material',{'p_ordem':id,'p_material':material_id,'p_quantidade':dados.quantidade,'p_acao':'atualizar'}))
@router.delete('/ordens/{id}/itens/{material_id}',status_code=204)
def apagar_item(id:Id,material_id:Id):
    executar(lambda db:db.rpc('tu_editar_item_material',{'p_ordem':id,'p_material':material_id,'p_quantidade':None,'p_acao':'excluir'}))
    return Response(status_code=204)
