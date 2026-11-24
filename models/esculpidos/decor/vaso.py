"""Vaso Botão – vaso de bojo redondo com gomos macios que giram suavemente, gargalo estreito e boca em pétalas.
Para flores secas ou artificiais (ou capa de vaso pequeno). Parede de 2 mm, fundo de 2,4 mm. 1 cor."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
g = Grade((-52, -52, 0), (52, 52, 132), passo)
X, Y, Z = g.x, g.y, g.z
H = 124.0
th = np.arctan2(Y, X)
rho = np.sqrt(X * X + Y * Y)
t = np.clip(Z / H, 0, 1)
# perfil: pé, bojo, gargalo e boca aberta
R = (28 + 20 * np.sin(np.pi * np.clip(t / 0.78, 0, 1)) ** 1.3 * (t < 0.78) + 0 * t
     - 8 * np.exp(-((t - 0.84) / 0.06) ** 2) + 9 * np.clip((t - 0.86) / 0.14, 0, 1) ** 1.6)
R = np.where(t < 0.04, 30 + (t - 0.04) * 40, R)
gomos = 12
tor = th + 0.9 * t ** 1.2                     # giro suave subindo
R = R + (1.6 + 1.4 * np.sin(np.pi * t)) * np.cos(gomos * tor)
# boca em pétalas (borda ondulada)
topo = H - 2.5 + 2.5 * np.cos(gomos * tor)
casca_ext = (rho - R) * 0.75
corpo = np.maximum(casca_ext, np.maximum(-Z, Z - topo))
oco = np.maximum((rho - (R - 2.0 / 0.75 * 0.75 * 1.0) + 2.0) * 0.75, 2.4 - Z)
corpo = menos(corpo, oco)
# filete no pé
corpo = smin(corpo, np.maximum(toro(g, (0, 0, 3.0), 29.5, 1.8, 1.0), -Z), 1.0)
corpo = np.maximum(corpo, -Z)
for k, v in exportar(g, {"c1": corpo}, os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "vaso"), faces=None).items():
    print(k, v)
