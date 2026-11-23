"""Render rápido de prova: python3 prova.py <nome> [el az] -> scratchpad/<nome>_prova.png (4 cores lado a lado)."""
import json, os, subprocess, sys
from PIL import Image
S = "/tmp/claude-0/-home-user-Mesa3D/fe3e95c1-33d4-58c9-a4b7-78c916ed0a7c/scratchpad"
n = sys.argv[1]
el, az = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (14, -24)
PRETO, BRANCO, VERMELHO = (0.018, 0.018, 0.02), (0.78, 0.78, 0.76), (0.42, 0.008, 0.012)
LARANJA, ROSA = (0.80, 0.18, 0.012), (0.85, 0.28, 0.42)
var = {"branco": dict(c1=BRANCO, c2=PRETO, c3=BRANCO, c4=LARANJA), "rosa": dict(c1=ROSA, c2=PRETO, c3=BRANCO, c4=VERMELHO),
       "preto": dict(c1=PRETO, c2=BRANCO, c3=PRETO, c4=LARANJA), "laranja": dict(c1=LARANJA, c2=PRETO, c3=BRANCO, c4=VERMELHO)}
d = os.path.abspath("stl")
partes = [dict(stl=f"{d}/{n}_{c}.stl", papel=c) for c in ["c1", "c2", "c3", "c4"] if os.path.exists(f"{d}/{n}_{c}.stl")]
job = dict(partes=partes, variantes={f"{S}/{n}_{k}.png": v for k, v in var.items()}, elevacao=el, azimute=az,
           tamanho=[700, 770], folga=1.02, amostras=32, estudio="vivo")
json.dump(job, open(f"{S}/{n}.json", "w"))
subprocess.run(["blender", "-b", "-noaudio", "-P", "/home/user/Mesa3D/site/render_blender.py", "--", f"{S}/{n}.json"], capture_output=True)
ims = [Image.open(f"{S}/{n}_{k}.png").convert("RGB") for k in var]
w, h = ims[0].size
s = Image.new("RGB", (w * 4, h))
for i, im in enumerate(ims):
    s.paste(im, (i * w, 0))
s.save(f"{S}/{n}_prova.png")
print(f"{S}/{n}_prova.png")
