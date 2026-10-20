"""Gera CSV desnormalizado de um GTFS publicado; não estima tempos ou atrasos."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import pandas as pd

ROOT = Path(__file__).resolve().parent
DESTINO = ROOT / 'data' / 'dados_publicos'
URL = 'https://github.com/benaytms/urbs-gtfs/releases/download/latest/gtfs_curitiba.zip'


def importar(arquivo, destino=DESTINO):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    with ZipFile(arquivo) as z:
        tabelas = {name: pd.read_csv(z.open(name), dtype='string', keep_default_na=False)
                   for name in ['routes.txt', 'trips.txt', 'agency.txt', 'feed_info.txt', 'calendar.txt']}
        linhas, programacoes = tabelas['routes.txt'], tabelas['trips.txt']
        assert not linhas.route_id.duplicated().any(), 'Código de linha duplicado na dimensão.'
        assert not programacoes.trip_id.duplicated().any(), 'Identificador de programação duplicado.'
        assert set(programacoes.route_id) <= set(linhas.route_id), 'Referência de linha ausente.'
        assert set(programacoes.service_id) <= set(tabelas['calendar.txt'].service_id), 'Tipo de serviço ausente.'
        assert set(linhas.agency_id) <= set(tabelas['agency.txt'].agency_id), 'Operadora ausente.'
        info = tabelas['feed_info.txt'].iloc[0]
        inicio = pd.to_datetime(info.feed_start_date, format='%Y%m%d').date().isoformat()
        fim = pd.to_datetime(info.feed_end_date, format='%Y%m%d').date().isoformat()
        dados = programacoes.merge(linhas, on='route_id', how='left', validate='many_to_one')
        dados = dados.merge(tabelas['agency.txt'][['agency_id', 'agency_name']], on='agency_id', validate='many_to_one')
        dados = dados.rename(columns={'trip_id': 'id_programacao', 'route_id': 'codigo_linha',
                                     'route_long_name': 'nome_linha', 'service_id': 'tipo_servico',
                                     'agency_name': 'operadora'})
        # Município vem da catalogação MDB-3225, não da geografia do TRANSURBAN.
        dados['cidade_fonte'] = 'Curitiba'
        dados['uf_fonte'] = 'PR'
        dados['periodo_feed_inicio'] = inicio
        dados['periodo_feed_fim'] = fim
        dados = dados[['id_programacao','codigo_linha','nome_linha','tipo_servico','operadora',
                       'cidade_fonte','uf_fonte','periodo_feed_inicio','periodo_feed_fim']]
        csv = destino / 'programacao_curitiba.csv'
        if csv.exists():
            raise FileExistsError('CSV já existe. Use outro destino para preservar o snapshot auditado.')
        dados.to_csv(csv,index=False,encoding='utf-8',lineterminator='\n')
        original = destino / 'originais'
        original.mkdir(exist_ok=True)
        hashes = {}
        for name in tabelas:
            content = z.read(name)
            (original/name).write_bytes(content)
            hashes[name] = hashlib.sha256(content).hexdigest()
        meta = {'natureza':'snapshot histórico de registros de programação publicados em GTFS comunitário',
                'feed_oficial':False, 'cidade':'Curitiba', 'uf':'PR',
                'publicador_gtfs':str(info.feed_publisher_name), 'publicador_url':str(info.feed_publisher_url),
                'origem_declarada_pelo_publicador':'dados abertos URBS espelhados pelo C3SL/UFPR',
                'origem_primaria_declarada_url':'https://dadosabertos.c3sl.ufpr.br/curitibaurbs/',
                'download_url':URL,
                'catalogo_url':'https://github.com/MobilityData/mobility-database-catalogs/blob/8c30f4b5dcc94946ec0696d097a1b1de0140cad4/catalogs/sources/gtfs/schedule/br-urbs-curitiba-onibus-gtfs-3225.json',
                'codigo_conversor_url':'https://github.com/benaytms/urbs-gtfs/tree/f10c931ba41a5e7edb60bc791f20dc74cfbd4981',
                'catalogo_is_official':'False',
                'coletado_em_utc':datetime.now(timezone.utc).isoformat(),
                'periodo_declarado_feed':{'inicio':inicio,'fim':fim},
                'zip_sha256':hashlib.sha256(Path(arquivo).read_bytes()).hexdigest(),
                'arquivos_originais_sha256':hashes,
                'csv_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),
                'registros_csv':len(dados),'linhas_distintas':int(dados.codigo_linha.nunique()),
                'transformacao':'Join many-to-one trips → routes → agency; seleção/renomeação; cidade/UF do catálogo; período de feed_info. Sem criar registros ou estimar medidas.',
                'licenca_codigo_conversor':'Apache-2.0; não confundir com licença dos dados',
                'licenca_dados':'Não declarada no feed; atribuição das fontes preservada.',
                'limitacoes':[
                    'Curitiba, não Maringá ou Sarandi. Estudo externo para validar a técnica do TRANSURBAN.',
                    'Feed comunitário: não é um GTFS oficial publicado pela URBS.',
                    'Período histórico declarado pelo feed: 28/09 a 05/10/2026; não representa oferta atual.',
                    'Cada linha CSV é um registro trip_id do GTFS convertido; não comprova viagem realizada, veículo ou passageiro.',
                    'Serviços dias úteis, sábado e domingo são categorias de programação; sua soma não é o total operado em um dia nem em uma semana.',
                    'O conversor propaga horários conhecidos para extremos do itinerário. stop_times.txt foi excluído da análise: não calcular duração ou atraso com ele.',
                    'Não há tempos observados, GPS ou atrasos medidos; não estimamos esses valores.',
                    'A qualidade verifica estrutura e consistência do snapshot, não audita a operação nem certifica a conversão feita pelo publicador.',
                    'Dados brutos primários URBS/C3SL não foram consultados diretamente nesta sessão; origem declarada conferida no código/README do conversor e catálogo independente.',
                ]}
        (destino/'fonte.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Importados {len(dados)} registros e {dados.codigo_linha.nunique()} códigos de linha do snapshot publicado. Nenhum atraso foi criado.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('arquivo',type=Path)
    p.add_argument('--destino',type=Path,default=DESTINO)
    a=p.parse_args()
    importar(a.arquivo,a.destino)
