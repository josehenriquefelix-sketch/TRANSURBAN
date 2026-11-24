"""Gera a visualização local do esquema a partir de metadados conferidos."""
from pathlib import Path
from html import escape
import json

BASE=Path(__file__).resolve().parents[1]
schema=json.loads((BASE/'docs/ESQUEMA_BANCO_ATUAL.json').read_text(encoding='utf-8-sig'))
assert schema['quantidade']==12
purposes={
 'cidade':'As duas cidades atendidas: Maringá e Sarandi.',
 'linha_onibus':'Códigos e nomes do catálogo documentado, vinculados à cidade.',
 'tu_perfil':'Nome, e-mail e hash do CPF da conta. A senha é gerenciada pelo Supabase Auth.',
 'tu_acesso':'Permissão profissional de motorista ou gestor e sua área de atendimento.',
 'tu_motorista':'Perfil do motorista autorizado e último ônibus informado.',
 'tu_viagem_operacional':'Motorista, linha, ônibus, sentido e início/fim da viagem.',
 'tu_posicao_atual':'Última posição compartilhada da viagem e precisão do aparelho.',
 'tu_manifestacao':'Notas, elogios, reclamações e histórico de respostas.',
 'tu_chamado':'Relatos privados, local opcional e histórico do atendimento.',
 'tu_alerta_operacional':'Avisos confirmados pela gestão, com local e prazo de validade.',
 'tu_favorito':'Linhas favoritas de cada usuário; chave composta evita repetição.',
 'tu_pedido_acesso':'Solicitação de vínculo, decisão e notificações do pedido.'}
rows=[];cards=[]
for t in schema['tabelas']:
    name=t['nome']; pk=', '.join(t['chave_primaria'])
    links='; '.join(r['campo']+' → '+r['tabela']+'.'+r['coluna'] for r in t['relacoes']) or '—'
    rows.append(f'| `{name}` | {purposes[name]} | {pk} | {links} |')
    fields=''.join('<li>'+escape(c['nome']+' · '+c['tipo']+(' · FK → '+c['fk'] if c['fk'] else ''))+'</li>' for c in t['campos'])
    cards.append('<article><h2>'+escape(name)+'</h2><p>'+escape(purposes[name])+'</p><strong>PK: '+escape(pk)+'</strong><ul>'+fields+'</ul></article>')
intro='''# Banco essencial — conferido em 24/11/2026

O esquema ativo `public` tem **12 tabelas**, todas com PK e RLS habilitada. As contas e senhas são gerenciadas no esquema interno `auth` do Supabase; essas tabelas internas não fazem parte das 12 tabelas do aplicativo.

| Tabela | Finalidade | PK | Relações públicas |
|---|---|---|---|
'''
ending='''

Os registros antigos foram preservados no schema privado `transurban_arquivo_20261124`, fora da Data API. Ele contém as 16 tabelas retiradas e duas cópias dos cadastros anteriores. Portanto, são 12 tabelas **ativas**, e o histórico não foi destruído. Não é uma redução para 12 objetos em toda a instalação do Supabase.

O cadastro ativo usa somente Maringá e Sarandi. O catálogo tem 66 linhas municipais de Maringá e 22 serviços/variantes metropolitanos que atendem Sarandi, com fonte registrada. Não se afirma cobertura municipal completa de Sarandi. A base CSV acadêmica continua sintética e separada.

Os históricos de atendimento ficam em `historico` no próprio registro; a fila de notificações fica em `notificacoes` no pedido. As funções PostgreSQL fazem atualizações atômicas e reservas de envio. Sem SMTP configurado, nada é marcado como enviado.

Para usar o mesmo projeto em outro computador, não recrie o banco. Clone o GitHub e configure o `.env` privado. Para um Supabase vazio: leia `database/README.md` antes de executar SQL.

A redução retirou os exercícios de estoque/pagamento e os horários/saldos fictícios da API principal. O código anterior está em `historico/`, para estudo. Essa decisão atende ao novo limite de 12 tabelas solicitado em 24/11; não equivale a cumprir um guia que exija estoque e ordens de material em funcionamento.
'''
(BASE/'docs/BANCO_CONFERIDO.md').write_text(intro+'\n'.join(rows)+ending,encoding='utf-8')
html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TRANSURBAN — 12 tabelas essenciais</title><style>body{font:16px/1.6 system-ui;max-width:1200px;margin:32px auto;padding:20px;background:#f4f7f6;color:#183339}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}article{background:white;padding:24px;border:1px solid #dce5e4;border-top:4px solid #0b4638;border-radius:14px}h1{line-height:1.2}h2{font-size:20px;overflow-wrap:anywhere}li{overflow-wrap:anywhere}a{color:#0b4638}</style><h1>TRANSURBAN — 12 tabelas essenciais</h1><p>Conferência: 24/11/2026. Estrutura do desenvolvedor, sem registros pessoais nem credenciais. Fora dos painéis de passageiros, motoristas e gestão. O histórico anterior foi preservado em schema privado; as tabelas internas do Supabase Auth não estão nesta contagem.</p><p><a href="https://supabase.com/dashboard/project/lsnpvokfnvyjkvqzkvof/editor">Abrir o Table Editor do Supabase</a></p><main>'''
(BASE/'ferramentas/estrutura_banco.html').write_text(html+''.join(cards)+'</main></html>',encoding='utf-8')
print('Documentação e visualização das 12 tabelas atualizadas.')
