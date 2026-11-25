"""Renderiza os giros 360° (quadros PNG verticais) dos produtos usados nos vídeos de gancho.
Uso: python3 videos/giros.py [nome ...]   ->  videos/.quadros/<nome>/0000.png ...   (precisa de blender)"""
import json, os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = os.path.join(R, "models", "esculpidos")
Q = os.path.join(R, "videos", ".quadros")
PRETO, BRANCO, VERMELHO = (0.018, 0.018, 0.02), (0.78, 0.78, 0.76), (0.42, 0.008, 0.012)
LARANJA, ROSA = (0.80, 0.18, 0.012), (0.85, 0.28, 0.42)
st = lambda pasta, nome, cs: [dict(stl=os.path.join(E, pasta, f"{nome}_{c}.stl"), papel=c, suave=True) for c in cs]
C4 = ["c1", "c2", "c3", "c4"]
GIROS = {
    "boo": (st("stl", "boo", C4), dict(c1=BRANCO, c2=PRETO, c3=BRANCO, c4=LARANJA), 12, 0.85),
    "monstrinho": (st("decor/stl", "monstrinho", C4), dict(c1=LARANJA, c2=PRETO, c3=BRANCO, c4=VERMELHO), 14, 0.85),
    "gatinho": (st("decor/stl", "gatinho", C4), dict(c1=PRETO, c2=BRANCO, c3=PRETO, c4=LARANJA), 24, 1.0),
    "porta_chaves": (st("decor/stl", "porta_chaves", ["c1", "c2"]), dict(c1=PRETO, c2=LARANJA), 38, 1.0),
    "dado": (st("sensoriais/stl", "dado", ["c1", "c2"]), dict(c1=ROSA, c2=PRETO), 22, 0.95),
}
QUADROS = 80
for nome in sys.argv[1:] or list(GIROS):
    partes, cores, el, folga = GIROS[nome]
    trab = os.path.join(Q, f"{nome}.json")
    os.makedirs(Q, exist_ok=True)
    json.dump(dict(partes=partes, variantes={"x": cores}, elevacao=el, azimute=-24, tamanho=[847, 1506], folga=folga,
                   amostras=24, estudio="creme", giro=dict(quadros=QUADROS, pasta=os.path.join(Q, nome))), open(trab, "w"))
    subprocess.run(["blender", "-b", "-noaudio", "-P", os.path.join(R, "site", "render_blender.py"), "--", trab], capture_output=True)
    print("ok", nome, len(os.listdir(os.path.join(Q, nome))), flush=True)
