#!/usr/bin/env python3
"""Monta o 3MF final da estátua: Joui (pintura do Meshy, escala 2x, cabelo preto) + base, pedra e nome."""
import zipfile, re, numpy as np, trimesh
P = open('/home/user/Mesa3D/models/decoracao/meshy/joui_projeto.txt').read().strip()
src = zipfile.ZipFile(P + '/multicolor/model.3mf')
t = src.read('3D/Objects/object_1.model').decode()
ESC, SINK = 2.0, 0.6

def esc(m):
    x, y, z = (float(v) for v in m.groups())
    return f'<vertex x="{x*ESC:.4f}" y="{y*ESC:.4f}" z="{z*ESC - SINK:.4f}"/>'
V = np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', t), float)
t = re.sub(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"\s*/>', esc, t)
# cabelo: triângulos vermelhos acima do rosto viram pretos
zv = V[:, 2]
def tri(m):
    a, b, c, pc = m.group(1), m.group(2), m.group(3), m.group(4) or ''
    zc = (zv[int(a)] + zv[int(b)] + zv[int(c)]) / 3
    if zc > 64.5 and pc and pc.count('4') >= max(pc.count('8'), pc.count('C')):
        pc = '0C'
    return f'<triangle v1="{a}" v2="{b}" v3="{c}"' + (f' paint_color="{pc}"' if pc else '') + '/>'
t = re.sub(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"(?: paint_color="([^"]*)")?\s*/>', tri, t)

def obj_xml(oid, path):
    m = trimesh.load(path)
    vs = '\n'.join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices)
    fs = '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return (f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n'
            f'    <triangles>\n{fs}\n    </triangles>\n   </mesh>\n  </object>\n'), len(m.faces)
extras = [(11, 'base.stl', 'Base', 3), (12, 'pedra.stl', 'Pedra', 3), (13, 'texto.stl', 'Nome JOUI', 1)]
blocos, faces = [], {}
for oid, f, _, _ in extras:
    x, n = obj_xml(oid, f); blocos.append(x); faces[oid] = n
t = t.replace(' </resources>', ''.join(blocos) + ' </resources>', 1)

hdr = src.read('3D/3dmodel.model').decode()
comp = '<component p:path="/3D/Objects/object_1.model" objectid="1" p:UUID="00010000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
novos = comp + ''.join(f'\n    <component p:path="/3D/Objects/object_1.model" objectid="{oid}" p:UUID="0001{oid:04d}-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' for oid, *_ in extras)
hdr = hdr.replace(comp, novos).replace('transform="1 0 0 0 1 0 0 0 1 125 125 0"', 'transform="1 0 0 0 1 0 0 0 1 128 128 8"')

cfg = src.read('Metadata/model_settings.config').decode()
cfg = cfg.replace('value="Object_1"/>\n    <metadata key="extruder"', 'value="Estatua Joui"/>\n    <metadata key="extruder"', 1)
cfg = cfg.replace('<metadata key="name" value="Object_1"/>\n      <metadata key="matrix"', '<metadata key="name" value="Joui"/>\n      <metadata key="matrix"', 1)
partes = ''.join(f'''    <part id="{oid}" subtype="normal_part">
      <metadata key="name" value="{nome}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="{ext}"/>
      <mesh_stat face_count="{faces[oid]}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
''' for oid, _, nome, ext in extras)
cfg = cfg.replace('    </part>\n  </object>', '    </part>\n' + partes + '  </object>', 1)

ps = src.read('Metadata/project_settings.config').decode()
ps = ps.replace('"#511B23FF"', '"#C0141CFF"').replace('"#A78D89FF"', '"#F2F2F2FF"').replace('"#130C16FF"', '"#151515FF"').replace('@BBL X1C', '@BBL A1')

out = zipfile.ZipFile('Estatua_Joui_3cores.3mf', 'w', zipfile.ZIP_DEFLATED)
for n in src.namelist():
    d = {'3D/Objects/object_1.model': t, '3D/3dmodel.model': hdr, 'Metadata/model_settings.config': cfg,
         'Metadata/project_settings.config': ps}.get(n)
    out.writestr(n, d if d is not None else src.read(n))
out.close()
print('ok')
