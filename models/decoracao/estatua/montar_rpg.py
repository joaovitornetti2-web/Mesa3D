import zipfile, re, numpy as np, trimesh
P = open('/home/user/Mesa3D/models/decoracao/meshy/joui_projeto.txt').read().strip()
src = zipfile.ZipFile(P + '/rpg_multicolor/model.3mf')
d = np.load('/tmp/claude-0/t3d/joui_rpg_fix.npz'); V, F, C = d['V'], d['F'], d['C']
ESC, SINK = 2.0, 0.8
cod = {1: '4', 2: '8', 3: '0C'}
vs = '\n'.join(f'     <vertex x="{x*ESC:.4f}" y="{y*ESC:.4f}" z="{z*ESC-SINK:.4f}"/>' for x, y, z in V)
fs = '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}" paint_color="{cod[k]}"/>' for (a, b, c), k in zip(F, C))
def obj(oid, vs, fs): return f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n    <triangles>\n{fs}\n    </triangles>\n   </mesh>\n  </object>\n'
def obj_stl(oid, f):
    m = trimesh.load(f)
    return obj(oid, '\n'.join(f'     <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices),
               '\n'.join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)), len(m.faces)
b, nb = obj_stl(11, 'rpg_base.stl'); tx, nt = obj_stl(13, 'rpg_texto.stl')
head = src.read('3D/Objects/object_1.model').decode().split('<resources>')[0]
model = head + '<resources>\n' + obj(1, vs, fs) + b + tx + ' </resources>\n <build/>\n</model>\n'
hdr = src.read('3D/3dmodel.model').decode()
comp = re.search(r'<component [^>]*objectid="1"[^>]*/>', hdr).group(0)
novos = comp + ''.join(f'\n    <component p:path="/3D/Objects/object_1.model" objectid="{o}" p:UUID="0001{o:04d}-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' for o in (11, 13))
hdr = hdr.replace(comp, novos)
hdr = re.sub(r'(<item objectid="2"[^>]*transform=")[^"]*"', r'\g<1>1 0 0 0 1 0 0 0 1 128 128 9"', hdr)
cfg = src.read('Metadata/model_settings.config').decode()
cfg = re.sub(r'<metadata face_count="\d+"/>', f'<metadata face_count="{len(F)+nb+nt}"/>', cfg, 1)
cfg = cfg.replace('<metadata key="name" value="Object_1"/>', '<metadata key="name" value="Estatua Joui"/>', 1)
partes = ''.join(f'''    <part id="{o}" subtype="normal_part">
      <metadata key="name" value="{n}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="{e}"/>
      <mesh_stat face_count="{fc}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
''' for o, n, e, fc in ((11, 'Base', 3, nb), (13, 'Nome JOUI', 1, nt)))
cfg = cfg.replace('    </part>\n  </object>', '    </part>\n' + partes + '  </object>', 1)
ps = src.read('Metadata/project_settings.config').decode()
ps = ps.replace('"#5E2122FF"', '"#C0141CFF"').replace('"#CCA696FF"', '"#F2F2F2FF"').replace('"#1D1C1DFF"', '"#151515FF"').replace('@BBL X1C', '@BBL A1')
out = zipfile.ZipFile('Estatua_Joui_RPG_3cores.3mf', 'w', zipfile.ZIP_DEFLATED)
for n in src.namelist():
    dd = {'3D/Objects/object_1.model': model, '3D/3dmodel.model': hdr, 'Metadata/model_settings.config': cfg, 'Metadata/project_settings.config': ps}.get(n)
    out.writestr(n, dd if dd is not None else src.read(n))
out.close(); print('ok', 'altura', round(float(V[:,2].max()*ESC-SINK),1))
