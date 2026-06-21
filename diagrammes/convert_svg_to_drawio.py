import xml.etree.ElementTree as ET
import uuid
import html
import re

def generate_id():
    return str(uuid.uuid4())

def parse_svg(svg_path, drawio_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Remove namespace from tags for easier parsing
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
            
    cells = []
    
    cells.append('<mxCell id="0" />')
    cells.append('<mxCell id="1" parent="0" />')
    
    for elem in root:
        tag = elem.tag
        
        if tag == 'rect':
            x = elem.get('x', '0')
            y = elem.get('y', '0')
            w = elem.get('width', '0')
            h = elem.get('height', '0')
            fill = elem.get('fill', 'none')
            stroke = elem.get('stroke', 'none')
            sw = elem.get('stroke-width', '1')
            sd = elem.get('stroke-dasharray')
            
            style = f"rounded=0;whiteSpace=wrap;html=1;"
            if fill != 'none': style += f"fillColor={fill};"
            else: style += "fillColor=none;"
            if stroke != 'none': style += f"strokeColor={stroke};"
            else: style += "strokeColor=none;"
            if sw != '1': style += f"strokeWidth={sw};"
            if sd: style += "dashed=1;"
            if elem.get('fill-opacity'): style += f"fillOpacity={float(elem.get('fill-opacity'))*100};"
            
            cells.append(f'<mxCell id="{generate_id()}" value="" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
            
        elif tag == 'text':
            x = float(elem.get('x', '0'))
            y = float(elem.get('y', '0'))
            text = elem.text or ''
            align = elem.get('text-anchor', 'start')
            fs = elem.get('font-size', '12')
            fw = elem.get('font-weight', 'normal')
            fst = elem.get('font-style', 'normal')
            fill = elem.get('fill', '#000')
            
            style = f"text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;rounded=0;fontSize={fs};fontColor={fill};"
            
            h = float(fs) + 4
            y_top = y - float(fs)
            
            w = 400
            if align == 'middle':
                style += "align=center;"
                x -= 200
            elif align == 'start':
                style += "align=left;"
            elif align == 'end':
                style += "align=right;"
                x -= 400
                
            if fw == 'bold': style += "fontStyle=1;"
            if fst == 'italic': style += "fontStyle=2;"
            
            text_escaped = html.escape(text)
            
            cells.append(f'<mxCell id="{generate_id()}" value="{text_escaped}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y_top}" width="{w}" height="{h}" as="geometry"/></mxCell>')
            
        elif tag == 'line':
            x1 = elem.get('x1', '0')
            y1 = elem.get('y1', '0')
            x2 = elem.get('x2', '0')
            y2 = elem.get('y2', '0')
            stroke = elem.get('stroke', '#000')
            sw = elem.get('stroke-width', '1')
            sd = elem.get('stroke-dasharray')
            marker_end = elem.get('marker-end')
            
            style = f"endArrow=none;html=1;strokeColor={stroke};strokeWidth={sw};"
            if sd: style += "dashed=1;"
            if marker_end:
                if 'arr-open' in marker_end:
                    style = style.replace('endArrow=none', 'endArrow=open')
                elif 'arr-red' in marker_end:
                    style = style.replace('endArrow=none', 'endArrow=block')
                elif 'arr' in marker_end:
                    style = style.replace('endArrow=none', 'endArrow=block;endFill=1')
            
            cells.append(f'<mxCell id="{generate_id()}" value="" style="{style}" edge="1" parent="1"><mxGeometry width="50" height="50" relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>')
            
        elif tag == 'path':
            d = elem.get('d', '')
            stroke = elem.get('stroke', '#000')
            sw = elem.get('stroke-width', '1')
            marker_end = elem.get('marker-end')
            
            style = f"endArrow=none;html=1;strokeColor={stroke};strokeWidth={sw};edgeStyle=orthogonalEdgeStyle;rounded=0;"
            if marker_end:
                if 'arr' in marker_end:
                    style = style.replace('endArrow=none', 'endArrow=block;endFill=1')
                    
            pts = re.findall(r'[ML]\s*([0-9.]+),([0-9.]+)', d)
            if len(pts) >= 2:
                sx, sy = pts[0]
                tx, ty = pts[-1]
                
                geom = f'<mxGeometry width="50" height="50" relative="1" as="geometry"><mxPoint x="{sx}" y="{sy}" as="sourcePoint"/><mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
                if len(pts) > 2:
                    geom += '<Array as="points">'
                    for px, py in pts[1:-1]:
                        geom += f'<mxPoint x="{px}" y="{py}"/>'
                    geom += '</Array>'
                geom += '</mxGeometry>'
                
                cells.append(f'<mxCell id="{generate_id()}" value="" style="{style}" edge="1" parent="1">{geom}</mxCell>')

    xml_out = f'''<mxfile host="Electron" modified="2024-01-01T00:00:00.000Z" agent="Mozilla/5.0" version="21.6.1" type="device">
  <diagram id="d1" name="Page-1">
    <mxGraphModel dx="1230" dy="930" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1230" pageHeight="930" math="0" shadow="0">
      <root>
        {chr(10).join(cells)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    with open(drawio_path, 'w', encoding='utf-8') as f:
        f.write(xml_out)

if __name__ == '__main__':
    parse_svg('C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/seq_workflow_infirmier.svg', 'C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/seq_workflow_infirmier.drawio')
    try:
        parse_svg('C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/copies_diagrammes/seq_workflow_infirmier.svg', 'C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/copies_diagrammes/seq_workflow_infirmier.drawio')
    except:
        pass
