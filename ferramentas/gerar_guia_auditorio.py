"""Reúne roteiro DS/IA para demonstração da API, sem criar slides."""
from pathlib import Path
import html
import importlib.util
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'apresentacoes/api-auditorio'
OUT.mkdir(exist_ok=True)
ds=(ROOT/'apresentacoes/roteiros_separados/ROTEIRO_DS_TRANSURBAN.md').read_text()
ia=(ROOT/'apresentacoes/roteiros_separados/ROTEIRO_IA_TRANSURBAN.md').read_text()
ds=ds[ds.index('## 2. Bruno'):]
ds=ds.replace('Obrigada pela atenção!”','Com isso, concluímos a parte de DS. Agora a Jullyany e a Camila vão apresentar a análise do CSV.”')
ia=ia[ia.index('## 1. Jullyany'):]
ia=ia.replace('“Bom dia, pessoal! Eu sou a Jullyany, e junto com a Camila vou apresentar a parte de Ciência de Dados do projeto TRANSURBAN.','“Agora vamos apresentar a parte de Ciência de Dados. Eu sou a Jullyany, e vou dividir essa explicação com a Camila.')
prefix='''# TRANSURBAN — Demonstração completa da API no auditório

Guia de falas e testes ao vivo • 20/10/2026 • Sem slides

Equipe: José Henrique, Bruno, Kauan, Gustavo, Ana Carolina, Jullyany e Camila. José Henrique pode operar todos os cliques. Bruno e Kauan mantêm as falas curtas. DS e IA estão separados em duas partes neste documento; os roteiros individuais continuam disponíveis. Reserve aproximadamente 14 a 18 minutos com cliques, ou ajuste ao tempo autorizado pela escola.

## O que mostrar ao público

A apresentação é da API funcionando no Swagger. Este documento orienta a equipe; não substitui a execução. O site é um complemento opcional e não é necessário para demonstrar DS e IA.

No computador que estiver executando o servidor, abra:

```text
http://127.0.0.1:8000/docs
```

Em cada operação: abra a rota, clique Try it out, preencha os dados quando necessário e clique Execute. Aguarde Server response e só então explique o resultado. Example Value não é evidência de execução.

## Preparação do operador, antes da apresentação

Extraia o pacote somente API e site. No VS Code, abra a pasta TRANSURBAN_API_SITE, onde está main.py. Requer Python 3.12 e internet para a primeira instalação. Não execute de dentro do ZIP. Se usar o pacote antigo com materiais, a pasta equivalente é backend_escola.

No Windows, execute um comando de cada vez:

```powershell
py -3.12 iniciar_apresentacao.py --preparar
py -3.12 iniciar_apresentacao.py --testar
py -3.12 iniciar_apresentacao.py --diagnostico
py -3.12 iniciar_apresentacao.py
```

No Linux, primeiro confira que python3 --version indica 3.12:

```bash
python3 iniciar_apresentacao.py --preparar
python3 iniciar_apresentacao.py --testar
python3 iniciar_apresentacao.py --diagnostico
python3 iniciar_apresentacao.py
```

Depois de Application startup complete, mantenha o terminal aberto. O inicializador usa SQLite local e preserva o .env: não precisa de senha Supabase. Não anuncie conexão remota que não foi comprovada. Se a porta 8000 estiver ocupada, use iniciar_apresentacao.py --port 8002 e troque a porta nos endereços.

Antes do público entrar, execute GET /health: esperado status ok e banco sqlite_local. Confirme zoom legível no telão e projeção da mesma tela. Não exiba .env, senhas ou autenticações. Depois da instalação, o Swagger e a análise do CSV local não precisam de internet; mapa, clima e cálculo de vias do site precisam.

Validação da entrega: 41 testes da suíte completa passaram em Linux, além do diagnóstico e do ensaio de duas contas do site. Esse número não é uma contagem exclusiva de DS ou de IA. Windows, GPS físico e projetor precisam ser ensaiados no equipamento real.

## Sequência rápida dos testes

| Etapa | Operação | Resultado esperado |
|---|---|---|
| Antes da fala | GET /health | 200, status ok e banco sqlite_local. |
| DS — cadastro | POST /cidades | 201; anote o id_cidade retornado. |
| DS — vínculo | POST /linhas | 201; use o ID real da cidade. |
| DS — consulta | GET /cidades e GET /linhas | 200; o cadastro está na lista, com o nome da cidade. |
| DS — proteção | POST /linhas com cidade ausente | 404; tentativa não salva. Confira antes que o ID não existe. |
| DS — validação | POST /cidades com nome só de espaços | 422; entrada rejeitada. |
| IA — origem | GET /ia/dados-publicos/fonte | Fonte comunitária histórica de Curitiba e período declarado. |
| IA — qualidade | GET /ia/dados-publicos/qualidade | Auditoria do CSV, identificadores e hashes. |
| IA — resumo | GET /ia/dados-publicos/resumo | 71.086 registros; 309 códigos; média 230,0518; mediana 162. |
| IA — comparação | GET /ia/dados-publicos/agrupamentos/{dimensao} | dimensao linha ou servico; parâmetro limite = 5 para o telão. |

Leia somente os parágrafos FALA. NA TELA e APOIO orientam o operador e as perguntas. Não anunciem resultado antes de ele aparecer na resposta real.

## Abertura geral — José Henrique

FALA: “Bom dia, pessoal! Eu sou o José Henrique e esta é a nossa equipe: Bruno, Kauan, Gustavo, Ana Carolina, Jullyany e Camila. Vamos apresentar o TRANSURBAN, um projeto acadêmico pensado para a mobilidade em Maringá e Sarandi.

FALA: Hoje vamos mostrar a API: a parte que recebe um pedido, verifica as informações, trabalha com os dados e devolve uma resposta.

FALA: A apresentação terá duas partes. Em DS, vamos cadastrar e consultar uma cidade e uma linha, mostrando a ligação entre as tabelas e o tratamento de entradas inválidas. Em IA, vamos analisar um CSV e explicar os indicadores que a fonte permite produzir.

FALA: Os cadastros da demonstração usam banco local. O código DEMO-20 é apenas um exemplo de teste. Na análise, utilizamos programação pública histórica de Curitiba, de origem comunitária: não são atrasos medidos de Maringá ou Sarandi.

FALA: O Bruno vai começar explicando o objetivo dos cadastros.”

## PARTE 1 — DS: cadastros, relacionamento e validações

'''
body=prefix+ds+'\n\n## PARTE 2 — IA: CSV, qualidade e indicadores\n\n'+ia
body+='''\n\n## Encerramento geral — José Henrique\n\nFALA: “Mostramos os pedidos chegando à API, as regras sendo aplicadas e os resultados sendo devolvidos. Em DS, verificamos cadastro, consulta, relacionamento e validação. Em IA, explicamos a fonte, conferimos o CSV e consultamos os indicadores. Os próximos passos dependem de fontes e integrações verificadas. Obrigado pela atenção!”\n\n## Se pedirem para ver o site\n\nAbra http://127.0.0.1:8000/app/ no mesmo computador. Use uma janela normal e outra anônima para contas de passageiro e motorista separadas. Demonstre somente o que já foi ensaiado: início da viagem, embarque/desembarque, relato de lotação e avaliação. GPS depende de permissão e sinal.\n\nFALA: “Este é um protótipo funcional da interface. As contas e avaliações são salvas no nosso banco local; as viagens são autodeclaradas. O mapa usa dados geográficos reais, mas o percurso escolhido não é um itinerário oficial da operadora. Pagamentos e vale-transporte são demonstrações, sem movimentar dinheiro.”\n\nA tarifa de referência urbana integral de Maringá é R$ 5,80 desde 12/07/2026, conforme notícia da Prefeitura documentada no sistema. Não generalize para Sarandi ou benefícios. O saldo da carteira não é um bilhete. Não afirme ligação ao GPS da frota, bilhetagem real ou previsão de chegada.\n'''
source=OUT/'GUIA_COMPLETO_API_AUDITORIO.md';source.write_text(body)
spec=importlib.util.spec_from_file_location('word',ROOT/'ferramentas/gerar_roteiros_docx.py')
word=importlib.util.module_from_spec(spec);spec.loader.exec_module(word);word.make(source)

fontdir=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('DejaVu','DejaVuSans.ttf'),('DejaVuBold','DejaVuSans-Bold.ttf'),('DejaVuMono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
styles=getSampleStyleSheet()
normal=ParagraphStyle('Texto',fontName='DejaVu',fontSize=10.6,leading=15,spaceAfter=7,splitLongWords=True)
head=ParagraphStyle('Secao',parent=normal,fontName='DejaVuBold',fontSize=14,leading=18,textColor=colors.HexColor('#153f4b'),spaceBefore=12,spaceAfter=8,keepWithNext=True)
title=ParagraphStyle('Titulo',parent=head,fontSize=22,leading=27)
small=ParagraphStyle('Apoio',parent=normal,fontSize=9.3,leading=13,textColor=colors.HexColor('#3e5d65'),backColor=colors.HexColor('#eef5f5'),borderPadding=5,spaceAfter=9)
cell=ParagraphStyle('Celula',parent=normal,fontSize=8.5,leading=12,spaceAfter=0)
code_style=ParagraphStyle('Codigo',fontName='DejaVuMono',fontSize=8.2,leading=11,spaceAfter=8,backColor=colors.HexColor('#f2f5f7'),borderPadding=5)
flow=[];lines=body.splitlines();i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line.startswith('```'):
        i+=1;block=[]
        while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
        flow.append(Preformatted('\n'.join(block),code_style));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[s.strip() for s in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?',x) for x in cells):rows.append([Paragraph(html.escape(x),cell) for x in cells])
            i+=1
        width=A4[0]-4*cm
        widths=[width*.24,width*.37,width*.39] if len(rows[0])==3 else [width*.35,width*.65]
        t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1eeee')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d2dfe1')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        flow.extend([t,Spacer(1,9)]);continue
    if line.startswith('# '):flow.append(Paragraph(html.escape(line[2:]),title))
    elif line.startswith('## '):flow.append(Paragraph(html.escape(line[3:]),head))
    else:
        text=html.escape(line)
        if line.startswith(('FALA:','JULLYANY — FALA:','CAMILA — FALA:')):
            label,rest=text.split(':',1);text='<b>'+label+':</b>'+rest
        flow.append(Paragraph(text,small if line.startswith(('NA TELA:','APOIO:','APOIO —','APOIO:')) else normal))
    i+=1

def footer(canvas,doc):
    canvas.setFont('DejaVu',8);canvas.setFillColor(colors.HexColor('#597079'))
    canvas.drawString(2*cm,1.1*cm,'TRANSURBAN • Guia de demonstração da API • Sem slides')
    canvas.drawRightString(A4[0]-2*cm,1.1*cm,str(doc.page))

SimpleDocTemplate(str(source.with_suffix('.pdf')),pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.7*cm,bottomMargin=1.8*cm,title='TRANSURBAN — Guia completo da API no auditório',author='Equipe TRANSURBAN').build(flow,onFirstPage=footer,onLaterPages=footer)
print('PDF e DOCX completos gerados.')
