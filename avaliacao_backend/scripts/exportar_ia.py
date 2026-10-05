"""Gera JSON dos cálculos. Não constitui evidência de requisição HTTP."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import analise

dest = ROOT / 'evidencias' / 'calculos_ia'
dest.mkdir(parents=True, exist_ok=True)
d, q = analise.carregar()
if d.empty or q['registros_excluidos'] or q['duplicatas_exatas_adicionais'] or q['codigos_com_nomes_divergentes']:
    raise ValueError('Corrija ou justifique a fonte antes de exportar indicadores.')
saidas = {'qualidade': q, 'resumo': analise.resumo(d, q), 'maiores_atrasos': analise.maiores(d)}
saidas.update({'por_' + dim: analise.agrupar(d, dim) for dim in analise.DIMENSOES})
for nome, valor in saidas.items():
    (dest / (nome + '.json')).write_text(json.dumps(valor, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
print(f'{len(saidas)} arquivos JSON calculados; fonte {q["sha256"]}')
