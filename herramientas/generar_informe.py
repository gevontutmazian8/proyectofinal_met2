"""Renderiza la fuente Markdown editable con índice y paginación."""
from pathlib import Path
import re
import textwrap
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Preformatted, KeepTogether, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents

RAIZ = Path(__file__).resolve().parents[1]
ANCHO, ALTO = A4
MARGEN = 48
UTIL = ANCHO - 2 * MARGEN


def configurar_fuentes():
    candidatos = [
        (Path('C:/Windows/Fonts/calibri.ttf'), Path('C:/Windows/Fonts/calibrib.ttf')),
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
    ]
    for regular, negrita in candidatos:
        if regular.exists() and negrita.exists():
            pdfmetrics.registerFont(TTFont('Texto', str(regular)))
            pdfmetrics.registerFont(TTFont('TextoBold', str(negrita)))
            pdfmetrics.registerFontFamily('Texto', normal='Texto', bold='TextoBold', italic='Texto', boldItalic='TextoBold')
            return 'Texto', 'TextoBold'
    return 'Helvetica', 'Helvetica-Bold'


NORMAL, BOLD = configurar_fuentes()
MONO = 'Courier'
for candidato in [Path('C:/Windows/Fonts/consola.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')]:
    if candidato.exists():
        pdfmetrics.registerFont(TTFont('CodigoUnicode', str(candidato)))
        MONO = 'CodigoUnicode'
        break
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('CuerpoTPI', fontName=NORMAL, fontSize=10.2, leading=14.2,
                          spaceAfter=7, allowWidows=0, allowOrphans=0, textColor=colors.HexColor('#202833')))
styles.add(ParagraphStyle('H1TPI', fontName=BOLD, fontSize=17, leading=21,
                          spaceBefore=9, spaceAfter=14, keepWithNext=True, textColor=colors.HexColor('#18334D')))
styles.add(ParagraphStyle('H2TPI', parent=styles['CuerpoTPI'], fontName=BOLD, fontSize=12.5,
                          leading=16, spaceBefore=12, keepWithNext=True))
styles.add(ParagraphStyle('H3TPI', parent=styles['CuerpoTPI'], fontName=BOLD, fontSize=10.5,
                          leading=14, spaceBefore=8, keepWithNext=True))
styles.add(ParagraphStyle('CeldaTPI', fontName=NORMAL, fontSize=7.8, leading=10.2, spaceAfter=0))
styles.add(ParagraphStyle('CodigoTPI', fontName=MONO, fontSize=7, leading=9,
                          leftIndent=7, spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle('PortadaTPI', fontName=BOLD, fontSize=27, leading=33,
                          textColor=colors.HexColor('#18334D'), spaceAfter=20))
styles.add(ParagraphStyle('PequenoTPI', parent=styles['CuerpoTPI'], fontSize=9, leading=12))


def inline(texto):
    texto = escape(texto)
    texto = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', texto)
    texto = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', texto)
    texto = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#285A80">\1</link>', texto)
    return texto


class Informe(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'H1TPI':
            titulo = flowable.getPlainText()
            clave = 'seccion_' + str(self.seq.nextf('secciones'))
            self.canv.bookmarkPage(clave)
            self.canv.addOutlineEntry(titulo, clave, 0, False)
            self.notify('TOCEntry', (0, titulo, self.page, clave))


def pie(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D5DDE5'))
    canvas.line(MARGEN, 43, ANCHO - MARGEN, 43)
    canvas.setFont(NORMAL, 8)
    canvas.setFillColor(colors.HexColor('#526273'))
    canvas.drawString(MARGEN, 30, 'Gevont Utmazian y Martín Maine | M25 C4-08 | Metodología de Sistemas II')
    canvas.drawRightString(ANCHO - MARGEN, 30, str(doc.page))
    if doc.page > 2:
        canvas.drawString(MARGEN, ALTO - 30, 'Gestión de solicitudes académicas - Informe técnico')
    canvas.restoreState()


def convertir(texto):
    lineas = texto.splitlines()
    salida = []
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        if not linea or linea == '---':
            i += 1
            continue
        if linea.startswith('```'):
            bloque = []
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith('```'):
                original = lineas[i].expandtabs(4)
                # Sólo ajuste visual: la fuente editable conserva las líneas originales.
                bloque.extend(textwrap.wrap(original, width=108, replace_whitespace=False,
                                            drop_whitespace=False, subsequent_indent='    ') or [''])
                i += 1
            codigo = Preformatted('\n'.join(bloque), styles['CodigoTPI'])
            salida.append(KeepTogether([codigo]) if len(bloque) <= 55 else codigo)
            i += 1
            continue
        if linea.startswith('|'):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith('|'):
                valores = [c.strip() for c in lineas[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in valores):
                    filas.append(valores)
                i += 1
            columnas = max(map(len, filas))
            datos = [[Paragraph(inline(c), styles['CeldaTPI']) for c in (fila + [''] * (columnas-len(fila)))] for fila in filas]
            if columnas == 6:
                pesos = [.06, .16, .20, .28, .09, .21]
            elif columnas == 5:
                pesos = [.07, .17, .10, .36, .30] if 'Severidad' in filas[0] else [.07, .33, .34, .13, .13]
            elif columnas == 4:
                pesos = [.21, .17, .32, .30]
            else:
                pesos = [1/columnas]*columnas
            tabla = Table(datos, colWidths=[UTIL*p for p in pesos], repeatRows=1, hAlign='LEFT')
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E5ECF2')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#BBC8D4')),
                ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FB')]),
            ]))
            salida.extend([tabla, Spacer(1,10)])
            continue
        if linea.startswith('# '):
            if salida:
                salida.append(PageBreak() if linea.startswith(('# 3.', '# 4.', '# 5.', '# 8.', '# 9.', '# 10.', '# 11.', '# 12.', '# 13.', '# Anexo')) else CondPageBreak(190))
            salida.append(Paragraph(inline(linea[2:]), styles['H1TPI']))
            i += 1
            continue
        if linea.startswith('## '):
            salida.append(Paragraph(inline(linea[3:]), styles['H2TPI']))
            i += 1
            continue
        if linea.startswith('### '):
            salida.append(Paragraph(inline(linea[4:]), styles['H3TPI']))
            i += 1
            continue
        if re.match(r'^[-*] ', linea) or re.match(r'^\d+\. ', linea):
            salida.append(Paragraph(inline(linea), styles['CuerpoTPI']))
            i += 1
            continue
        parrafo = [linea]
        i += 1
        while i < len(lineas) and lineas[i].strip() and not lineas[i].strip().startswith(('#', '|', '```', '- ', '* ')):
            parrafo.append(lineas[i].strip())
            i += 1
        contenido = '<br/>'.join(map(inline, parrafo)) if len(parrafo) == 6 and parrafo[0].startswith('Se construyó') else inline(' '.join(parrafo))
        salida.append(Paragraph(contenido, styles['CuerpoTPI']))
    return salida


def main():
    fuente = RAIZ / 'informe/Informe_TPI_MS2_Gevont_Utmazian.md'
    destino = fuente.with_suffix('.pdf')
    documento = Informe(str(destino), pagesize=A4, leftMargin=MARGEN, rightMargin=MARGEN,
                        topMargin=52, bottomMargin=55, title='TPI - Metodología de Sistemas II',
                        author='Gevont Utmazian y Martín Maine - asistencia de ChatGPT/Codex declarada')
    marco = Frame(MARGEN, 55, UTIL, ALTO-107, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    documento.addPageTemplates(PageTemplate(id='Informe', frames=marco, onPage=pie))
    flujo = [Spacer(1,55), Paragraph('UNIVERSIDAD TECNOLÓGICA NACIONAL', styles['H2TPI']),
             Paragraph('Tecnicatura Universitaria en Programación a Distancia', styles['CuerpoTPI']),
             Spacer(1,35), Paragraph('Metodología de Sistemas II', styles['H2TPI']),
             Paragraph('Trabajo Práctico<br/>Integrador', styles['PortadaTPI']),
             Paragraph('Evolución profesional de un sistema existente: calidad, deuda técnica, refactoring y revisión técnica', styles['H2TPI']),
             Spacer(1,24), Paragraph('Sistema de Gestión de Solicitudes Académicas', styles['CuerpoTPI']),
             Spacer(1,25), Paragraph('<b>Integrantes:</b> Gevont Utmazian, Martín Maine<br/><b>Comisión:</b> M25 C4-08<br/><b>Año académico:</b> 2026', styles['CuerpoTPI']),
             Paragraph('Fecha de entrega: 08/11/2026.', styles['PequenoTPI']),
             Spacer(1,20), Paragraph('Informe técnico. El uso de IA se detalla en el apartado correspondiente.', styles['PequenoTPI']),
             PageBreak(), Paragraph('Índice', styles['H2TPI'])]
    indice = TableOfContents()
    indice.levelStyles = [ParagraphStyle('IndiceTPI',fontName=NORMAL,fontSize=11,leading=17,spaceBefore=6)]
    flujo.extend([indice, PageBreak()])
    flujo.extend(convertir(fuente.read_text(encoding='utf-8')))
    documento.multiBuild(flujo)
    print(destino)


if __name__ == '__main__':
    main()
