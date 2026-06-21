import base64
import urllib.parse
import os

def create_base64_drawio(svg_path, drawio_path):
    with open(svg_path, "rb") as f:
        svg_data = f.read()

    b64_svg = base64.b64encode(svg_data).decode('utf-8')
    # Use base64 format which drawio supports, but ensure correct exact shape syntax
    # Actually, Draw.io prefers URL encoded SVGs for embedded SVGs
    svg_str = svg_data.decode('utf-8')
    url_encoded = urllib.parse.quote(svg_str)
    data_uri = f"data:image/svg+xml,{url_encoded}"

    drawio_xml = f"""<mxfile host="Electron">
  <diagram id="diagram_1" name="Page-1">
    <mxGraphModel dx="1230" dy="930" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1230" pageHeight="930" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image={data_uri}" vertex="1" parent="1">
          <mxGeometry x="0" y="0" width="1230" height="930" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    with open(drawio_path, "w", encoding="utf-8") as f:
        f.write(drawio_xml)

if __name__ == '__main__':
    create_base64_drawio('C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/seq_workflow_infirmier.svg', 'C:/Users/Lenovo/APPLICATION-D-AIDE-AU-DIAGNOSTIC-DE-MALADES-V2/diagrammes/seq_workflow_infirmier_exact.drawio')
