import xml.etree.ElementTree as ET
import html
import re

def parse_svg(svg_path, drawio_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
            
    cells = []
    cells.append('<mxCell id="0" />')
    cells.append('<mxCell id="1" parent="0" />')
    
    cell_id = 2
    
    for elem in root:
        tag = elem.tag
        
        if tag == 'rect':
            w = float(elem.get('width', '0'))
            h = float(elem.get('height', '0'))
            if w >= 1200 and h >= 900:
                continue
                
            x = float(elem.get('x', '0'))
            y = float(elem.get('y', '0'))
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
            if elem.get('fill-opacity'): style += f"fillOpacity={int(float(elem.get('fill-opacity'))*100)};"
            
            cells.append(f'<mxCell id="{cell_id}" value="" style="{style}" vertex="1" parent="1"><mxGeometry x="{int(x)}" y="{int(y)}" width="{int(w)}" height="{int(h)}" as="geometry"/></mxCell>')
            cell_id += 1
            
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
            
            cells.append(f'<mxCell id="{cell_id}" value="{text_escaped}" style="{style}" vertex="1" parent="1"><mxGeometry x="{int(x)}" y="{int(y_top)}" width="{int(w)}" height="{int(h)}" as="geometry"/></mxCell>')
            cell_id += 1
            
        elif tag == 'line':
            x1 = float(elem.get('x1', '0'))
            y1 = float(elem.get('y1', '0'))
            x2 = float(elem.get('x2', '0'))
            y2 = float(elem.get('y2', '0'))
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
            
            cells.append(f'<mxCell id="{cell_id}" value="" style="{style}" edge="1" parent="1"><mxGeometry width="50" height="50" relative="1" as="geometry"><mxPoint x="{int(x1)}" y="{int(y1)}" as="sourcePoint"/><mxPoint x="{int(x2)}" y="{int(y2)}" as="targetPoint"/></mxGeometry></mxCell>')
            cell_id += 1
            
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
                
                geom = f'<mxGeometry width="50" height="50" relative="1" as="geometry"><mxPoint x="{int(float(sx))}" y="{int(float(sy))}" as="sourcePoint"/><mxPoint x="{int(float(tx))}" y="{int(float(ty))}" as="targetPoint"/>'
                if len(pts) > 2:
                    geom += '<Array as="points">'
                    for px, py in pts[1:-1]:
                        geom += f'<mxPoint x="{int(float(px))}" y="{int(float(py))}"/>'
                    geom += '</Array>'
                geom += '</mxGeometry>'
                
                cells.append(f'<mxCell id="{cell_id}" value="" style="{style}" edge="1" parent="1">{geom}</mxCell>')
                cell_id += 1

    xml_out = f'''<mxfile host="Electron">
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
    except Exception as e:
        pass
