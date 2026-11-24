"""Conferência real de leitura, login e atendimento; não mostra credenciais."""
import json
import logging
import sys
from pathlib import Path
from uuid import UUID

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
logging.disable(logging.CRITICAL)
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from backend.main import app
from backend.esquema import consultar
from backend.database import get_supabase

checks = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print('OK ' + name, flush=True)

env = dotenv_values(BASE / 'backend/.env')
schema = consultar()
expected = {'cidade','linha_onibus','tu_perfil','tu_acesso','tu_motorista','tu_favorito',
            'tu_viagem_operacional','tu_posicao_atual','tu_manifestacao','tu_chamado',
            'tu_alerta_operacional','tu_pedido_acesso'}
tables = {t['nome']: t for t in schema['tabelas']}
check('Exatamente 12 tabelas ativas na Data API', set(tables) == expected)
check('As 12 tabelas têm chave primária', all(t['chave_primaria'] for t in tables.values()))
check('Linha mantém FK para cidade', any(r['tabela']=='cidade' for r in tables['linha_onibus']['relacoes']))
check('Viagem mantém FK para motorista', any(r['tabela']=='tu_motorista' for r in tables['tu_viagem_operacional']['relacoes']))
db=get_supabase()
cities=db.table('cidade').select('id_cidade,nome').execute().data
check('Cadastro ativo contém somente as duas cidades reais',{c['nome'] for c in cities}=={'Maringá','Sarandi'} and len(cities)==2)
city_names={c['id_cidade']:c['nome'] for c in cities}
lines=db.table('linha_onibus').select('id_cidade,codigo,nome').execute().data
catalog=json.loads((BASE/'data/catalogo_publico_verificado.json').read_text(encoding='utf-8-sig'))
actual={(city_names[l['id_cidade']],l['codigo'],l['nome']) for l in lines}
documented={(l['cidade_principal'],l['codigo'],l['nome']) for l in catalog['linhas']}
check('88 linhas e variantes reconciliadas com o catálogo documentado',actual==documented and len(lines)==88)
schema['conferido_em'] = '2026-11-24'
(BASE/'docs/ESQUEMA_BANCO_ATUAL.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2),encoding='utf-8')

with TestClient(app) as client:
    for path in ['/', '/motorista/', '/gestao/', '/docs', '/dados/docs', '/acessos.html', '/mobilidade/catalogo', '/mobilidade/viagens']:
        check('Página ou API acessível: '+path, client.get(path).status_code == 200)
    for path in ['/backend/.env','/.env','/gestao/banco.html','/estudo/materiais.html','/portal/recargas']:
        check('Arquivo ou módulo retirado não exposto: '+path, client.get(path).status_code in [404,405])
    for role in ['passageiro','motorista','gestor']:
        response = client.post('/auth/login',json={'identificador':env['DEMO_EMAIL'],'senha':env['DEMO_PASSWORD'],'tipo_acesso':role})
        check('Login real: '+role, response.status_code == 200)
        check('Permissão confirmada: '+role, role in client.get('/auth/me').json()['papeis'])
        client.post('/auth/logout')
        check('Logout encerra sessão: '+role, client.get('/auth/me').status_code == 401)

    # Uma mensagem privada, explicitamente de teste, e remoção só deste registro.
    client.post('/auth/login',json={'identificador':env['DEMO_EMAIL'],'senha':env['DEMO_PASSWORD'],'tipo_acesso':'gestor'})
    db = get_supabase()
    call_id = None
    try:
        response = client.post('/atendimento/passageiro/chamados', json={'cidade':'Maringá','categoria':'Acessibilidade',
            'assunto':'TESTE AUTOMATIZADO DESCARTÁVEL', 'mensagem':'Validação técnica temporária. Não representa ocorrência real.'})
        check('Chamado privado gravado no banco real',response.status_code==201)
        call_id = str(UUID(response.json()['id']))
        response = client.put('/atendimento/gestao/chamados/'+call_id,json={'status':'respondido','resposta':'Resposta técnica descartável da conferência do sistema.'})
        check('Resposta da gestão gravada',response.status_code==200)
        record = db.table('tu_chamado').select('historico').eq('id',call_id).single().execute().data
        check('Histórico incorporado preserva resposta e autor',len(record['historico'])==1 and bool(record['historico'][0]['autor_id']))
        check('Relato respondido disponível ao autor',any(c['id']==call_id and c['status']=='respondido' for c in client.get('/atendimento/meus-chamados').json()))
        check('Fila de notificações acessível sem tabela extra',client.get('/atendimento/gestao/notificacoes').status_code==200)
    finally:
        if call_id:
            db.table('tu_chamado').delete().eq('id',call_id).execute()
        client.post('/auth/logout')
    check('Registro temporário removido',not db.table('tu_chamado').select('id').eq('id',call_id).execute().data)

report = {'data':'2026-11-24','resultado':'OK','quantidade':len(checks),'verificacoes':checks,
          'tabelas_ativas':12,'historico':'Tabelas anteriores preservadas em schema privado; fora da API.',
          'limites':['Não comprova GPS físico, entrega de e-mail sem SMTP ou operação oficial da frota.',
                     'Não substitui testar a rede e as permissões do computador da escola.']}
(BASE/'docs/VALIDACAO_ENTREGA_20261124.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'resultado':'OK','verificacoes':len(checks),'tabelas':12}),flush=True)
