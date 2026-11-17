# Monta o 3MF de 3 cores da caveira-torre: malha colorida do Meshy (escala 2,1) + rampas/piso internos como peça extra.
# Uso: python3 montar_caveira.py <model.3mf do Meshy> <caveira_fix.npz> <rampas.stl> <saida.3mf>
import zipfile, re, sys, numpy as np, trimesh
src = zipfile.ZipFile(sys.argv[1]); d = np.load(sys.argv[2]); V, F, C = d['V'] * 2.1, d['F'], d['C']
cod = {1: '4', 2: '8', 3: '0C'}   # 1 preto, 2 branco, 3 vermelho
xyz = lambda P: '\n'.join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in P)
def obj(oid, vs, fs): return f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n    <triangles>\n{fs}\n    </triangles>\n   </mesh>\n  </object>\n'
fs = '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}" paint_color="{cod[k]}"/>' for (a, b, c), k in zip(F, C))
r = trimesh.load(sys.argv[3]); nb = len(r.faces)
rb = obj(11, xyz(r.vertices), '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in r.faces))
head = src.read('3D/Objects/object_1.model').decode().split('<resources>')[0]
model = head + '<resources>\n' + obj(1, xyz(V), fs) + rb + ' </resources>\n <build/>\n</model>\n'
hdr = src.read('3D/3dmodel.model').decode()
comp = re.search(r'<component [^>]*objectid="1"[^>]*/>', hdr).group(0)
hdr = hdr.replace(comp, comp + '\n    <component p:path="/3D/Objects/object_1.model" objectid="11" p:UUID="00010011-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
hdr = re.sub(r'(<item objectid="2"[^>]*transform=")[^"]*"', r'\g<1>1 0 0 0 1 0 0 0 1 128 128 0"', hdr)
cfg = src.read('Metadata/model_settings.config').decode()
cfg = re.sub(r'<metadata face_count="\d+"/>', f'<metadata face_count="{len(F)+nb}"/>', cfg, count=1)
cfg = cfg.replace('<metadata key="name" value="Object_1"/>', '<metadata key="name" value="Caveira Torre de Dados"/>', 1)
cfg = cfg.replace('    </part>\n  </object>', f'''    </part>
    <part id="11" subtype="normal_part">
      <metadata key="name" value="Rampas e piso internos"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="2"/>
      <mesh_stat face_count="{nb}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>''', 1)
ps = src.read('Metadata/project_settings.config').decode()
cores = re.search(r'"filament_colour": \[(.*?)\]', ps, re.S).group(1)
novas = iter(['"#151515FF"', '"#F2F2F2FF"', '"#C0141CFF"'])
ps = ps.replace(cores, re.sub(r'"#[0-9A-F]{8}"', lambda m: next(novas), cores)).replace('@BBL X1C', '@BBL A1')
out = zipfile.ZipFile(sys.argv[4], 'w', zipfile.ZIP_DEFLATED)
for n in src.namelist():
    dd = {'3D/Objects/object_1.model': model, '3D/3dmodel.model': hdr, 'Metadata/model_settings.config': cfg, 'Metadata/project_settings.config': ps}.get(n)
    out.writestr(n, dd if dd is not None else src.read(n))
out.close(); print('ok', V.max(0) - V.min(0))
