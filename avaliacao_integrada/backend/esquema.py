"""Lê metadados da Data API sem devolver registros, chaves ou tokens."""
import os
import re
import httpx


def organizar(documento):
    tabelas=[]
    for nome,definicao in sorted(documento.get('definitions',{}).items()):
        campos=[];primaria=[];relacoes=[]
        for campo,dados in definicao.get('properties',{}).items():
            descricao=dados.get('description','')
            pk='<pk/>' in descricao
            if pk:primaria.append(campo)
            fk=re.search(r"<fk table='([^']+)' column='([^']+)'/>",descricao)
            destino=(fk.group(1)+'.'+fk.group(2)) if fk else None
            if fk:relacoes.append({'campo':campo,'tabela':fk.group(1),'coluna':fk.group(2)})
            campos.append({'nome':campo,'tipo':dados.get('format',dados.get('type','')),'obrigatorio':campo in definicao.get('required',[]),'pk':pk,'fk':destino})
        tabelas.append({'nome':nome,'chave_primaria':primaria,'relacoes':relacoes,'campos':campos})
    return {'tabelas':tabelas,'quantidade':len(tabelas),'limite':'Metadados de public expostos pela Data API; não inclui dados das contas nem detalhes internos do esquema auth.'}


def consultar():
    url=os.environ['SUPABASE_URL'].rstrip('/')
    chave=os.environ['SUPABASE_KEY']
    resposta=httpx.get(url+'/rest/v1/',headers={'apikey':chave,'Authorization':'Bearer '+chave,'Accept':'application/openapi+json'},timeout=20)
    resposta.raise_for_status()
    return organizar(resposta.json())
