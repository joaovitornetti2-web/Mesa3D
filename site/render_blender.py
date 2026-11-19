"""Render de produto para o site (Cycles, CPU), num estúdio escuro com luz vermelha de contorno.

Uso: blender -b -P site/render_blender.py -- trabalho.json
trabalho.json:
{
  "partes": [{"stl": "a.stl", "papel": "c1"}, ...],   # STLs já na posição montada (mm)
  "variantes": {"saida.png": {"c1": [r,g,b], "c2": [...]}, ...},   # cor linear por papel
  "elevacao": 28, "azimute": -35, "folga": 1.15, "amostras": 48, "tamanho": [1200, 960],
  "textura": {"c1": false}   # opcional: true usa as cores de vértice do arquivo (malha do Meshy)
}
"""
import json
import math
import sys

import bpy
from mathutils import Vector

cfg = json.load(open(sys.argv[sys.argv.index("--") + 1]))

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = cfg.get("amostras", 48)
cena.cycles.use_denoising = False
cena.cycles.adaptive_threshold = 0.02
cena.cycles.max_bounces = 6
cena.render.resolution_x, cena.render.resolution_y = cfg.get("tamanho", [1200, 960])
cena.render.film_transparent = False
vt = [i.identifier for i in cena.view_settings.bl_rna.properties["view_transform"].enum_items]
cena.view_settings.view_transform = "AgX" if "AgX" in vt else "Filmic"
cena.view_settings.look = "None"


def material(nome, cor, rough=0.46):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rough
    for k in ("Specular IOR Level", "Specular"):
        if k in b.inputs:
            b.inputs[k].default_value = 0.35
    return m


mats = {}
objs = []
for p in cfg["partes"]:
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=p["stl"])
    else:
        bpy.ops.import_mesh.stl(filepath=p["stl"])
    o = bpy.context.selected_objects[0]
    o.scale = (0.01, 0.01, 0.01)   # mm -> unidades de cena (1 u = 10 cm), luzes em escala humana
    papel = p["papel"]
    if papel not in mats:
        mats[papel] = material(papel, (0.5, 0.5, 0.5))
    o.data.materials.append(mats[papel])
    if p.get("suave"):
        bpy.ops.object.shade_smooth()
    else:
        bpy.ops.object.shade_flat()
    objs.append(o)
bpy.context.view_layer.update()

# caixa envolvente
cantos = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
mn = Vector((min(c.x for c in cantos), min(c.y for c in cantos), min(c.z for c in cantos)))
mx = Vector((max(c.x for c in cantos), max(c.y for c in cantos), max(c.z for c in cantos)))
centro = (mn + mx) / 2
raio = (mx - mn).length / 2
# apoia no chão (z = 0) e centraliza em xy
for o in objs:
    o.location += Vector((-centro.x, -centro.y, -mn.z))
centro = Vector((0, 0, (mx.z - mn.z) / 2))

# chão infinito escuro (ciclorama) com leve brilho
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
chao = bpy.context.object
mchao = material("chao", (0.006, 0.006, 0.006), 0.75)
chao.data.materials.append(mchao)

mundo = bpy.data.worlds.new("mundo")
cena.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.004, 0.004, 1)
mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 1


def luz(nome, tipo, energia, cor, pos, tam=1.0):
    d = bpy.data.lights.new(nome, tipo)
    d.energy = energia
    d.color = cor
    if tipo == "AREA":
        d.size = tam
    o = bpy.data.objects.new(nome, d)
    cena.collection.objects.link(o)
    o.location = pos
    dirc = (centro - Vector(pos)).normalized()
    o.rotation_euler = dirc.to_track_quat("-Z", "Y").to_euler()
    return o


r = max(raio, 0.2)
luz("principal", "AREA", 260 * r * r, (1.0, 0.95, 0.88), (-2.2 * r, -2.6 * r, 2.8 * r), 2.4 * r)
luz("preenchimento", "AREA", 45 * r * r, (0.85, 0.9, 1.0), (2.8 * r, -1.6 * r, 1.2 * r), 3 * r)
luz("contorno", "AREA", 300 * r * r, (1.0, 0.05, 0.03), (1.0 * r, 3.0 * r, 3.2 * r), 1.2 * r)
luz("contorno2", "AREA", 120 * r * r, (1.0, 0.05, 0.03), (-2.6 * r, 2.2 * r, 2.4 * r), 1.0 * r)
luz("topo", "AREA", 60 * r * r, (1.0, 1.0, 1.0), (0, 0, 4 * r), 2 * r)

# câmera
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 70
cam = bpy.data.objects.new("cam", cam_d)
cena.collection.objects.link(cam)
cena.camera = cam
el, az = math.radians(cfg.get("elevacao", 28)), math.radians(cfg.get("azimute", -35))
fov = min(cam_d.angle_x, cam_d.angle_y * cena.render.resolution_y / cena.render.resolution_x * cena.render.resolution_x / cena.render.resolution_y)
fov = 2 * math.atan(18 / cam_d.lens) if cena.render.resolution_x >= cena.render.resolution_y else 2 * math.atan(18 * cena.render.resolution_x / cena.render.resolution_y / cam_d.lens)
dist = raio * cfg.get("folga", 1.15) / math.sin(fov / 2)
cam.location = centro + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
cam.rotation_euler = (centro - cam.location).to_track_quat("-Z", "Y").to_euler()
cam_d.clip_start, cam_d.clip_end = 0.001, dist * 10

for saida, cores in cfg["variantes"].items():
    for papel, cor in cores.items():
        mats[papel].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*cor, 1)
    cena.render.filepath = saida
    bpy.ops.render.render(write_still=True)
    print("RENDER", saida, flush=True)
