"""Anel Giratório – mecânica de models/sensoriais/sensoriais.scad (aro com crista em V, faixa que gira, impresso já montado,
DECOR=false); a faixa de fora ganha em relevo uma ciranda de fantasminhas com estrelinhas entre eles.
c1 aro de dentro · c2 faixa de fora (com os fantasminhas). Uso: python3 anel.py [passo] [aro 17|19|21]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, trimesh
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.07
ARO = int(sys.argv[2]) if len(sys.argv) > 2 else 19
RE = ARO / 2 + 1.6 + 3.6           # raio de fora da faixa
W = 10.0
g = Grade((-RE - 2, -RE - 2, -0.5), (RE + 2, RE + 2, W + 0.5), passo)
X, Y, Z = g.x, g.y, g.z
rho = np.sqrt(X * X + Y * Y); th = np.arctan2(Y, X)
N = 6
a = (th % (2 * np.pi / N)) - np.pi / N                     # ângulo local em cada fantasminha
s_ = a * RE                                                # mm ao longo da faixa
zc = Z - W / 2
cab = np.sqrt(s_ ** 2 + (zc - 0.8) ** 2) - 2.6
corpo2 = np.maximum(np.abs(s_) - 2.6, np.maximum(zc - 0.8, -zc - 2.6))
gh = np.minimum(cab, corpo2)
for dz in (-1.73, 0, 1.73):
    gh = np.maximum(gh, -(np.sqrt((s_ - dz) ** 2 + (zc + 3.0) ** 2) - 0.9))
olhos = np.minimum(np.sqrt((s_ - 0.95) ** 2 + (zc - 1.0) ** 2) - 0.45, np.sqrt((s_ + 0.95) ** 2 + (zc - 1.0) ** 2) - 0.45)
gh = np.maximum(gh, -olhos)                                 # olhinhos vazados
b = ((th + np.pi / N) % (2 * np.pi / N)) - np.pi / N        # estrelinha entre dois fantasminhas
sb = b * RE
estr = np.sqrt(sb ** 2 + zc ** 2)
ab = np.arctan2(zc, sb)
estr = estr - 2.0 * (0.45 + 0.55 * np.abs(np.cos(2.5 * (ab - np.pi / 2))) ** 4)
arte = np.minimum(gh, estr)
rel = np.maximum(np.maximum(arte, rho - RE - 0.7), RE - 0.4 - rho)
rel = np.maximum(rel, np.abs(zc) - W / 2 + 0.6)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
m_rel = malha(g, rel, suaviza=2)
mec = trimesh.load(os.path.join(out, f"anel_mec_{ARO}.stl"))
partes = sorted(mec.split(only_watertight=False), key=lambda p: p.bounds[1][0])
aro, faixa = partes[0], partes[-1]
faixa = trimesh.util.concatenate([faixa, m_rel])
suf = "" if ARO == 19 else f"_{ARO}"
aro.export(os.path.join(out, f"anel{suf}_c1.stl")); faixa.export(os.path.join(out, f"anel{suf}_c2.stl"))
print(ARO, len(aro.faces), len(faixa.faces))
