# Monta o 3MF de 3 cores do Deus da Morte (Meshy multicolor) sobre a base que encaixa no telhado da torre.
# Uso pessoal: o modelo vem da arte oficial e a saída fica fora do git.
import zipfile, re, sys, numpy as np, trimesh
P = sys.argv[1]                       # pasta do projeto Meshy (com cores2/model.3mf)
NPZ = sys.argv[2]                     # malha com as cores já corrigidas (V, F, C)
ALT = 65.0                            # altura final da figura (mm)
src = zipfile.ZipFile(P + '/cores2/model.3mf')
d = np.load(NPZ); V, F, C = d['V'], d['F'], d['C']
esc = ALT / V[:, 2].max()
pes = V[V[:, 2] < 3]; cx, cy = (pes.min(0)[:2] + pes.max(0)[:2]) / 2
V = np.c_[(V[:, 0] - cx) * esc, (V[:, 1] - cy) * esc, V[:, 2] * esc + 3.0 - 0.6]   # pés afundam 0,6 mm na base
cod = {1: '4', 2: '8', 3: '0C'}
vs = '\n'.join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in V)
fs = '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}" paint_color="{cod[k]}"/>' for (a, b, c), k in zip(F, C))
def obj(oid, vs, fs): return f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n    <triangles>\n{fs}\n    </triangles>\n   </mesh>\n  </object>\n'
m = trimesh.load('/home/user/Mesa3D/models/torre/stl/base_deus.stl')
b = obj(11, '\n'.join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices),
        '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)); nb = len(m.faces)
head = src.read('3D/Objects/object_1.model').decode().split('<resources>')[0]
model = head + '<resources>\n' + obj(1, vs, fs) + b + ' </resources>\n <build/>\n</model>\n'
hdr = src.read('3D/3dmodel.model').decode()
comp = re.search(r'<component [^>]*objectid="1"[^>]*/>', hdr).group(0)
hdr = hdr.replace(comp, comp + '\n    <component p:path="/3D/Objects/object_1.model" objectid="11" p:UUID="00010011-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
hdr = re.sub(r'(<item objectid="2"[^>]*transform=")[^"]*"', r'\g<1>1 0 0 0 1 0 0 0 1 128 128 0"', hdr)
cfg = src.read('Metadata/model_settings.config').decode()
cfg = re.sub(r'<metadata face_count="\d+"/>', f'<metadata face_count="{len(F)+nb}"/>', cfg, 1)
cfg = cfg.replace('<metadata key="name" value="Object_1"/>', '<metadata key="name" value="Deus da Morte"/>', 1)
cfg = cfg.replace('    </part>\n  </object>', f'''    </part>
    <part id="11" subtype="normal_part">
      <metadata key="name" value="Base (encaixe no telhado)"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="1"/>
      <mesh_stat face_count="{nb}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>''', 1)
ps = src.read('Metadata/project_settings.config').decode()
ps = ps.replace('"#1A1B1BFF"', '"#151515FF"').replace('"#B9B7B4FF"', '"#F2F2F2FF"').replace('"#595A59FF"', '"#C0141CFF"').replace('@BBL X1C', '@BBL A1')
out = zipfile.ZipFile(sys.argv[3], 'w', zipfile.ZIP_DEFLATED)
for n in src.namelist():
    dd = {'3D/Objects/object_1.model': model, '3D/3dmodel.model': hdr, 'Metadata/model_settings.config': cfg, 'Metadata/project_settings.config': ps}.get(n)
    out.writestr(n, dd if dd is not None else src.read(n))
out.close()
np.savez('/tmp/claude-0/t3d/deus_final.npz', V=V, F=F, C=C)
print('ok altura total', round(float(V[:, 2].max()), 1), 'larg', (V.max(0) - V.min(0)).round(1))
