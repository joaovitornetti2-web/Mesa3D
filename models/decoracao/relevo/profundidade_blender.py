"""Mapa de profundidade frontal de um modelo (OBJ do Meshy) para baixo-relevo.
blender -b -P profundidade_blender.py -- modelo.obj saida.npz LARG_MM ALT_MM PX_MM
Câmera ortográfica olhando de -Y para +Y (frente do modelo no Blender). Grava profundidade em mm."""
import sys, bpy, json
from array import array
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
obj, out, W, H, PX = a[0], a[1], float(a[2]), float(a[3]), float(a[4])
bpy.ops.wm.read_factory_settings(use_empty=True)
(bpy.ops.wm.obj_import if hasattr(bpy.ops.wm, "obj_import") else bpy.ops.import_scene.obj)(filepath=obj)
o = [x for x in bpy.context.scene.objects if x.type == "MESH"][0]
# o importador gira o objeto (Y-up -> Z-up) sem mexer nos vértices; a BVH usa coordenadas locais
bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(o, dg)
M = o.matrix_world
pts = [M @ v.co for v in o.data.vertices]
lo = [min(p[k] for p in pts) for k in range(3)]
hi = [max(p[k] for p in pts) for k in range(3)]
# escala: altura da figura = 1.06 x altura da placa (a base do busto passa da moldura e é cortada)
s = H * 1.06 / (hi[2] - lo[2])
cx = (lo[0] + hi[0]) / 2
ztop = hi[2]
nx, nz = int(W / PX), int(H / PX)
NAN = float("nan")
prof = array("f", [NAN]) * (nz * nx)
y0 = lo[1] - 1.0
d = Vector((0, 1, 0))
for i in range(nz):
    z = ztop - (i + 0.5) * PX / s + (H * 0.02) / s          # pequena folga no topo
    for j in range(nx):
        x = cx + ((j + 0.5) * PX - W / 2) / s
        hit = bvh.ray_cast(Vector((x, y0, z)), d)
        if hit[0] is not None:
            prof[i * nx + j] = (hit[0].y - lo[1]) * s           # mm a partir do ponto mais à frente
with open(out + ".bin", "wb") as f:
    prof.tofile(f)
json.dump({"nx": nx, "nz": nz, "px": PX, "escala": s}, open(out + ".json", "w"))
print("ok", nx, nz, "acertos", sum(1 for v in prof if v == v))
