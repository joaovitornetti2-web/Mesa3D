"""Foto de abertura do site: várias peças juntas na mesma mesa (render único).
Uso: python3 videos/cena_turma.py  ->  site/img/hero_turma.webp e hero_turma_cel.webp"""
import json, os, subprocess
import numpy as np, trimesh
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = os.path.join(R, "models", "esculpidos")
T = os.path.join(R, "videos", ".quadros", "cena")
os.makedirs(T, exist_ok=True)
PRETO, BRANCO, VERMELHO = (0.018, 0.018, 0.02), (0.78, 0.78, 0.76), (0.42, 0.008, 0.012)
LARANJA, ROSA = (0.80, 0.18, 0.012), (0.85, 0.28, 0.42)
# (pasta, nome, cores por papel, posição x y em mm, giro em graus)
PECAS = [
    ("decor/stl", "monstrinho", dict(c1=LARANJA, c2=PRETO, c3=BRANCO, c4=VERMELHO), (-70, 55), 15),
    ("stl", "boo", dict(c1=BRANCO, c2=PRETO, c3=BRANCO, c4=LARANJA), (8, 40), -5),
    ("stl", "morceguinho", dict(c1=PRETO, c2=BRANCO, c3=PRETO, c4=LARANJA), (78, 48), -20),
    ("stl", "gosminha", dict(c1=ROSA, c2=PRETO, c3=BRANCO, c4=VERMELHO), (-38, -22), 10),
    ("stl", "caveirinha", dict(c1=BRANCO, c2=PRETO, c3=BRANCO, c4=ROSA), (30, -18), -12),
    ("sensoriais/stl", "piao", dict(c1=LARANJA, c2=PRETO, c4=PRETO), (-100, -12), 0),
    ("sensoriais/stl", "chaveiro", dict(c1=ROSA, c2=PRETO, c3=BRANCO, c4=VERMELHO), (82, -26), -15),
    ("sensoriais/stl", "dado", dict(c1=BRANCO, c2=PRETO), (-4, -62), 30),
]
partes, cores = [], {}
for pasta, nome, cs, (x, y), giro in PECAS:
    for papel, cor in cs.items():
        f = os.path.join(E, pasta, f"{nome}_{papel}.stl")
        if not os.path.exists(f):
            continue
        m = trimesh.load(f)
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(giro), [0, 0, 1]))
        m.apply_translation([x, y, 0])
        out = os.path.join(T, f"{nome}_{papel}.stl")
        m.export(out)
        partes.append(dict(stl=out, papel=f"{nome}_{papel}", suave=True))
        cores[f"{nome}_{papel}"] = cor
for saida, tam, el, folga in (("hero_turma", [1882, 1176], 16, 0.86), ("hero_turma_cel", [1176, 1412], 18, 0.98)):
    png = os.path.join(T, saida + ".png")
    trab = os.path.join(T, saida + ".json")
    json.dump(dict(partes=partes, variantes={png: cores}, elevacao=el, azimute=-8, tamanho=tam, folga=folga, amostras=96, estudio="vivo"), open(trab, "w"))
    subprocess.run(["blender", "-b", "-noaudio", "-P", os.path.join(R, "site", "render_blender.py"), "--", trab], capture_output=True)
    im = Image.open(png).convert("RGB")
    im.save(os.path.join(R, "site", "img", saida + ".webp"), quality=86)
    print("ok", saida, im.size, flush=True)
