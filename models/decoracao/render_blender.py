"""Render realista de um relicário (Cycles, CPU). Uso:
blender -b -P render_blender.py -- <elemento> <pasta_saida> <arquivo.png> [amostras]
Precisa de <pasta>/<e>_corpo.stl, <e>_tampa.stl, <e>_medalhao_cor1.stl, <e>_medalhao_cor2.stl"""
import sys, math, os
import bpy
from mathutils import Matrix
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
e, pasta, saida = argv[0], argv[1], argv[2]
amostras = int(argv[3]) if len(argv) > 3 else 64
# opcional: placas de personagens "nome@angulo,..." (pasta personagens/saida)
PLACAS = [(x.split("@")[0], float(x.split("@")[1])) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] else []
CORPO = argv[5] if len(argv) > 5 else f"{e}_corpo.stl"
H, ZT, ASSENTO = 34.0, 12.0, 2.0
CORES = {"sangue": ((0.018, 0.018, 0.02), (0.55, 0.02, 0.03)),
         "morte": ((0.018, 0.018, 0.02), (0.82, 0.82, 0.80)),
         "medo": ((0.80, 0.80, 0.78), (0.018, 0.018, 0.02)),
         "energia": ((0.018, 0.018, 0.02), (0.82, 0.82, 0.80))}
COR3 = (0.55, 0.02, 0.03)   # 3ª cor (vermelho) quando existir *_medalhao_cor3.stl
c1, c2 = CORES[e]

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = amostras
cena.cycles.use_denoising = False
cena.render.resolution_x, cena.render.resolution_y = 1400, 1100
cena.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in cena.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"


def material(nome, cor, rough=0.42):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rough
    return m


def importar(caminho, mat, matriz=Matrix()):
    bpy.ops.wm.stl_import(filepath=caminho) if hasattr(bpy.ops.wm, "stl_import") else bpy.ops.import_mesh.stl(filepath=caminho)
    o = bpy.context.selected_objects[0]
    o.matrix_world = matriz @ o.matrix_world
    o.data.materials.append(mat)
    bpy.ops.object.shade_flat()
    return o


m1, m2 = material("cor1", c1), material("cor2", c2, 0.35)
corpo = importar(f"{pasta}/{CORPO}", m1)
bpy.context.view_layer.update()
H = corpo.dimensions.z                 # altura real do corpo (muda por tamanho)
esc = corpo.dimensions.x / 82.07       # escala xy (82.07 mm = base do tamanho de referência)
ZT, ASSENTO = ZT * esc, ASSENTO * esc
# tampa: volta da posição de impressão para a de uso: (x,y,z) -> (-x, y, ZT - z), depois sobe H
virar = Matrix.Translation((0, 0, H + 0.2 + ZT)) @ Matrix.Rotation(math.pi, 4, "Y")
importar(f"{pasta}/{e}_tampa.stl", m1, virar)
sobe = Matrix.Translation((0, 0, H + 0.2 + ZT - ASSENTO))
importar(f"{pasta}/{e}_medalhao_cor1.stl", m1, sobe)
importar(f"{pasta}/{e}_medalhao_cor2.stl", m2, sobe)
import os
if os.path.exists(f"{pasta}/{e}_medalhao_cor3.stl"):
    importar(f"{pasta}/{e}_medalhao_cor3.stl", material("cor3", COR3, 0.35), sobe)

# placas: x da placa -> tangente, y -> altura, z (relevo) -> para fora da parede
if PLACAS:
    mp = [material("p1", (0.018, 0.018, 0.02)), material("p2", (0.55, 0.02, 0.03), 0.35), material("p3", (0.82, 0.82, 0.80), 0.35)]
    r_fundo = (38 - 0.8) * esc; z0 = 8.5 * esc + 0.2
    base = "/home/user/Mesa3D/models/decoracao/personagens/saida"
    for nome, ang in PLACAS:
        M = (Matrix.Rotation(math.radians(ang), 4, "Z") @ Matrix.Translation((r_fundo, 0, z0))
             @ Matrix(((0, 0, 1, 0), (1, 0, 0, -17.4), (0, 1, 0, 0), (0, 0, 0, 1))))
        rel = f"/home/user/Mesa3D/models/decoracao/relevo/saida/{nome}_relevo_cor1.stl"
        if os.path.exists(rel):   # baixo-relevo (Meshy): preto + branco
            for i, mat in ((1, mp[0]), (2, mp[2])):
                importar(rel.replace("_cor1", f"_cor{i}"), mat, M)
        else:
            for i in (1, 2, 3):
                importar(f"{base}/{nome}_placa_cor{i}.stl", mp[i - 1], M)

# altura total da cena (inclui figura na tampa) para enquadrar
bpy.context.view_layer.update()
ALTO = max((o.matrix_world @ mathutils.Vector(c)).z for o in bpy.context.scene.objects if o.type == "MESH" for c in o.bound_box)
print("ALTO", ALTO)

# chão e fundo
bpy.ops.mesh.primitive_plane_add(size=800, location=(0, 0, 0))
bpy.context.object.data.materials.append(material("chao", (0.11, 0.105, 0.10), 0.6))
mundo = bpy.data.worlds.new("mundo"); cena.world = mundo; mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.012, 0.014, 1)
mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0


def luz(nome, pos, energia, tam, cor=(1, 1, 1)):
    d = bpy.data.lights.new(nome, "AREA"); d.energy = energia; d.size = tam; d.color = cor
    o = bpy.data.objects.new(nome, d); cena.collection.objects.link(o); o.location = pos
    dirv = -o.location.normalized()
    o.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()


luz("principal", (-160, -140, 220), 9.0e5, 120)
luz("recorte", (170, 120, 120), 4.5e5, 80, (0.85, 0.9, 1.0))
luz("preenchimento", (160, -200, 60), 1.4e5, 150)

cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 85
cam = bpy.data.objects.new("cam", cam_d); cena.collection.objects.link(cam); cena.camera = cam
cam.location = mathutils.Vector((-55, -275, 175)) * max(1.0, ALTO / 85.0)
cam_d.clip_end = 5000
alvo = cam.location.copy(); alvo.z = 0
import mathutils
dirv = (mathutils.Vector((0, 0, ALTO * 0.5)) - cam.location).normalized()
cam_d.lens = 85
cam.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()

print("CAM", tuple(cam.location), "clip", cam_d.clip_end)
cena.render.filepath = saida
bpy.ops.render.render(write_still=True)
