"""Gera documentos editáveis separados a partir dos roteiros Markdown revisados."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1] / 'apresentacoes/roteiros_separados'


def shade(paragraph, fill):
    pr=paragraph._p.get_or_add_pPr()
    node=OxmlElement('w:shd');node.set(qn('w:fill'),fill);pr.append(node)


def make(source):
    doc=Document()
    sec=doc.sections[0]
    sec.page_width=Cm(21);sec.page_height=Cm(29.7)
    sec.top_margin=Cm(1.8);sec.bottom_margin=Cm(1.8)
    sec.left_margin=Cm(2);sec.right_margin=Cm(2)
    normal=doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(12)
    normal.paragraph_format.space_after=Pt(7)
    normal.paragraph_format.line_spacing=1.12
    for name,size in [('Title',24),('Heading 1',16),('Heading 2',13)]:
        style=doc.styles[name];style.font.name='Calibri';style.font.size=Pt(size)
        style.font.color.rgb=RGBColor.from_string('153F4B')
        style.paragraph_format.keep_with_next=True
    h=sec.header.paragraphs[0];h.text='TRANSURBAN  |  API  |  ROTEIRO SEM SLIDES'
    h.style='Caption'
    f=sec.footer.paragraphs[0];f.alignment=2
    f.add_run('20/10/2026  •  ')
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
    doc.core_properties.author='Equipe TRANSURBAN'
    doc.core_properties.title=source.stem.replace('_',' ')
    doc.core_properties.subject='Roteiro de apresentação — DS e IA em documentos independentes'
    lines=source.read_text(encoding='utf-8').splitlines()
    i=0;code=False
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            code=not code;i+=1;continue
        if code:
            p=doc.add_paragraph();p.paragraph_format.space_after=Pt(1)
            p.paragraph_format.line_spacing=1
            r=p.add_run(line or ' ');r.font.name='Consolas';r.font.size=Pt(10)
            shade(p,'F2F5F7');i+=1;continue
        if not line.strip():i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[x.strip() for x in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',x) for x in cells):rows.append(cells)
                i+=1
            if not rows:continue
            table=doc.add_table(rows=1,cols=len(rows[0]));table.style='Light Shading Accent 1'
            for j,cell in enumerate(rows[0]):table.rows[0].cells[j].text=cell
            trPr=table.rows[0]._tr.get_or_add_trPr();repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
            for row in rows[1:]:
                cells=table.add_row().cells
                for j,text in enumerate(row):cells[j].text=text
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        p.paragraph_format.space_after=Pt(4)
                        for r in p.runs:r.font.size=Pt(10.5)
            doc.add_paragraph();continue
        if line.startswith('# '):doc.add_heading(line[2:],0)
        elif line.startswith('## '):doc.add_heading(line[3:],1)
        else:
            p=doc.add_paragraph()
            match=re.match(r'(JULLYANY — FALA:|CAMILA — FALA:|FALA DE APOIO:|FALA, antes de clicar:|FALA:|NA TELA:|APOIO(?: — [^:]+)?:)(.*)',line)
            if match:
                label,text=match.groups()
                r=p.add_run(label+' ');r.bold=True
                p.add_run(text.strip())
                if label.startswith(('FALA','JULLYANY','CAMILA')):
                    p.paragraph_format.left_indent=Cm(.2)
                    for run in p.runs:run.font.size=Pt(12.5)
                else:
                    shade(p,'EAF3F3')
                    for run in p.runs:run.font.size=Pt(10.5)
            else:p.add_run(line)
        i+=1
    dest=source.with_suffix('.docx');doc.save(dest)
    # Reabertura verifica estrutura OOXML e que todos os títulos foram preservados.
    reopened=Document(dest)
    for title in [x[3:] for x in lines if x.startswith('## ')]:
        assert title in [p.text for p in reopened.paragraphs],title
    print(dest.name, '—',len(reopened.paragraphs),'parágrafos,',len(reopened.tables),'tabelas')


if __name__=='__main__':
    for name in ['ROTEIRO_DS_TRANSURBAN.md','ROTEIRO_IA_TRANSURBAN.md']:make(ROOT/name)
