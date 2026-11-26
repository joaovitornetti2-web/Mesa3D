"""Render rápido de prova das coleções: python3 prova.py <colecao>/<nome> [el az] -> scratchpad/<nome>_prova.png
Mostra 4 combinações de cor lado a lado (c1 corpo, c2 escuro/metal, c3 claro, c4 destaque)."""
import json, os, subprocess, sys
from PIL import Image
S = os.environ.get("PROVA_DIR", "/tmp/claude-0/-home-user-Mesa3D/aaf0298c-c06f-5f0d-adb0-1be93a15b87b/scratchpad/prova")
os.makedirs(S, exist_ok=True)
RAIZ = os.path.dirname(os.path.abspath(__file__))
col, n = sys.argv[1].rsplit("/", 1)
el, az = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (22, -28)
PRETO, BRANCO, VERMELHO = (0.018, 0.018, 0.02), (0.78, 0.78, 0.76), (0.42, 0.008, 0.012)
LARANJA, ROSA, CINZA = (0.80, 0.18, 0.012), (0.85, 0.28, 0.42), (0.2, 0.21, 0.22)
var = {"preto": dict(c1=PRETO, c2=CINZA, c3=BRANCO, c4=VERMELHO, c5=LARANJA),
       "branco": dict(c1=BRANCO, c2=PRETO, c3=BRANCO, c4=VERMELHO, c5=LARANJA),
       "vermelho": dict(c1=VERMELHO, c2=PRETO, c3=BRANCO, c4=LARANJA, c5=PRETO),
       "laranja": dict(c1=LARANJA, c2=PRETO, c3=BRANCO, c4=VERMELHO, c5=PRETO)}
d = os.path.join(RAIZ, col, "stl")
partes = [dict(stl=f"{d}/{n}_{c}.stl", papel=c, suave=True) for c in ["c1", "c2", "c3", "c4", "c5"] if os.path.exists(f"{d}/{n}_{c}.stl")]
papeis = {p["papel"] for p in partes}
job = dict(partes=partes, variantes={f"{S}/{n}_{k}.png": {c: v[c] for c in papeis} for k, v in var.items()}, elevacao=el, azimute=az,
           tamanho=[640, 700], folga=float(os.environ.get("FOLGA", 1.02)), amostras=24, estudio="vivo")
json.dump(job, open(f"{S}/{n}.json", "w"))
r = subprocess.run(["blender", "-b", "-noaudio", "-P", os.path.join(os.path.dirname(RAIZ), "..", "site", "render_blender.py"), "--", f"{S}/{n}.json"],
                   capture_output=True, text=True)
if r.returncode:
    print(r.stdout[-1500:], r.stderr[-1500:])
ims = [Image.open(f"{S}/{n}_{k}.png").convert("RGB") for k in var]
w, h = ims[0].size
s = Image.new("RGB", (w * 4, h))
for i, im in enumerate(ims):
    s.paste(im, (i * w, 0))
s.save(f"{S}/{n}_prova.png")
print(f"{S}/{n}_prova.png")
