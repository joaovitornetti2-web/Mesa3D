"""Prova de miniatura em 3 vistas (frente, lado, costas), uma cor de argila cinza clara.
Uso: python3 vistas.py <pasta>/<nome> [<pasta>/<nome> ...]  ->  scratchpad/prova/<nome>_vistas.png (todas lado a lado)"""
import json, os, subprocess, sys
from PIL import Image

S = "/tmp/claude-0/-home-user-Mesa3D/aaf0298c-c06f-5f0d-adb0-1be93a15b87b/scratchpad/prova"
os.makedirs(S, exist_ok=True)
RAIZ = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(RAIZ, "..", "..", "..", "site", "render_blender.py")
ARGILA = {"c1": (0.55, 0.55, 0.53), "c2": (0.12, 0.12, 0.13), "c3": (0.55, 0.55, 0.53), "c4": (0.45, 0.06, 0.05), "c5": (0.55, 0.3, 0.05)}
VISTAS = [("frente", 8, -12), ("lado", 8, -95), ("costas", 8, 160)]
linhas = []
for alvo in sys.argv[1:]:
    pasta, nome = alvo.rsplit("/", 1)
    d = os.path.join(RAIZ, pasta, "stl")
    partes = [dict(stl=f"{d}/{nome}_{c}.stl", papel=c, suave=True) for c in ARGILA if os.path.exists(f"{d}/{nome}_{c}.stl")]
    ims = []
    for v, el, az in VISTAS:
        png = f"{S}/{nome}_{v}.png"
        job = dict(partes=partes, variantes={png: {p["papel"]: ARGILA[p["papel"]] for p in partes}}, elevacao=el, azimute=az,
                   tamanho=[520, 700], folga=float(os.environ.get("FOLGA", 0.66)), amostras=20, estudio="vivo")
        jf = f"{S}/{nome}_{v}.json"
        json.dump(job, open(jf, "w"))
        r = subprocess.run(["blender", "-b", "-noaudio", "-P", RENDER, "--", jf], capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-800:])
        ims.append(Image.open(png).convert("RGB"))
    w, h = ims[0].size
    lin = Image.new("RGB", (w * 3, h))
    for i, im in enumerate(ims):
        lin.paste(im, (i * w, 0))
    linhas.append(lin)
w, h = linhas[0].size
tudo = Image.new("RGB", (w, h * len(linhas)))
for i, l in enumerate(linhas):
    tudo.paste(l, (0, i * h))
out = f"{S}/vistas.png"
tudo.save(out)
print(out)
