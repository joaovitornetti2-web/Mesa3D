"""Foto de vitrine de miniatura: python3 foto.py <pasta>/<nome> ... -> scratchpad/prova/<nome>_foto.png (frente 3/4 e costas 3/4).
Cores de impressão: c1 figura (cinza-azulado), c2 armas/objetos (grafite), c3 base (pedra), c4 detalhe (vermelho sangue)."""
import json, os, subprocess, sys
from PIL import Image
S = "/tmp/claude-0/-home-user-Mesa3D/aaf0298c-c06f-5f0d-adb0-1be93a15b87b/scratchpad/prova"
os.makedirs(S, exist_ok=True)
RAIZ = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(RAIZ, "..", "..", "..", "site", "render_blender.py")
COR = {"c1": (0.50, 0.53, 0.56), "c2": (0.035, 0.035, 0.04), "c3": (0.30, 0.27, 0.23), "c4": (0.42, 0.008, 0.012), "c5": (0.8, 0.45, 0.05)}
for alvo in sys.argv[1:]:
    pasta, nome = alvo.rsplit("/", 1)
    d = os.path.join(RAIZ, pasta, "stl")
    partes = [dict(stl=f"{d}/{nome}_{c}.stl", papel=c, suave=True) for c in COR if os.path.exists(f"{d}/{nome}_{c}.stl")]
    ims = []
    for v, el, az in (("a", 12, -30), ("b", 14, 145)):
        png = f"{S}/{nome}_{v}.png"
        job = dict(partes=partes, variantes={png: {p["papel"]: COR[p["papel"]] for p in partes}}, elevacao=el, azimute=az,
                   tamanho=[600, 800], folga=float(os.environ.get("FOLGA", 0.62)), amostras=48, estudio="vivo")
        jf = f"{S}/{nome}_{v}.json"
        json.dump(job, open(jf, "w"))
        r = subprocess.run(["blender", "-b", "-noaudio", "-P", RENDER, "--", jf], capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-800:])
        ims.append(Image.open(png).convert("RGB"))
    w, h = ims[0].size
    t = Image.new("RGB", (w * 2, h))
    for i, im in enumerate(ims):
        t.paste(im, (i * w, 0))
    t.save(f"{S}/{nome}_foto.png")
    print(f"{S}/{nome}_foto.png", flush=True)
