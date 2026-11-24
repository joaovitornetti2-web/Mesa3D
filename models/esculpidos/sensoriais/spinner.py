"""Spinner Ciranda dos Gatinhos – três cabecinhas de gato girando em volta de um rolamento 608 (22 × 7 mm).
Carinhas em relevo só no topo (troca de cor nas últimas camadas). Tampinhas com estrelinha em cima e embaixo.
c1 corpo · c2 carinhas · c3 rolamento (só na foto) · c4 bochechas e tampinhas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
FURO, H = 22.15, 7.6
g = Grade((-44, -44, 0), (44, 44, 13), passo)
X, Y, Z = g.x, g.y, g.z
rho = np.sqrt(X * X + Y * Y); th = np.arctan2(Y, X)

def c2d(cx, cy, r):
    return np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) - r
def smin2(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)

forma = rho - 16.5
rosto, boch = [], []
for k in range(3):
    a = np.radians(90 + k * 120)
    ca, sa = np.cos(a), np.sin(a)
    U = X * ca + Y * sa; V = -X * sa + Y * ca          # U para fora, V de lado
    cab = np.sqrt((U - 28) ** 2 + (V / 1.08) ** 2) - 11.0
    for s_ in (-1, 1):                                  # orelhas
        e = np.radians(s_ * 38)
        ux, vy = 28 + 9.5 * np.cos(e), 9.5 * np.sin(e)
        du, dv = U - ux, V - vy
        lu = du * np.cos(e) + dv * np.sin(e); lv = -du * np.sin(e) + dv * np.cos(e)
        orelha = np.maximum(np.abs(lv) * 1.0 + lu * 0.62 - 3.6, -lu - 2.0) - 1.0
        cab = smin2(cab, orelha, 1.2)
    forma = smin2(forma, cab, 5.0)
    ex = lambda uu, vv: (uu * ca - vv * sa, uu * sa + vv * ca)
    for vv, rr in ((-4.4, 2.2), (4.4, 2.2)):
        x0, y0 = ex(29.5, vv)
        rosto.append(np.sqrt((((X - x0) * ca + (Y - y0) * sa) / 1.25) ** 2 + ((-(X - x0) * sa + (Y - y0) * ca)) ** 2) - rr)
    x0, y0 = ex(25.6, 0)                                # nariz
    rosto.append(c2d(x0, y0, 1.1))
    for s_ in (-1, 1):                                  # boquinha "w"
        x0, y0 = ex(24.2, s_ * 1.3)
        rosto.append(np.maximum(np.abs(c2d(x0, y0, 1.3)) - 0.42, (X * ca + Y * sa) - 24.2))
        for d in (-1, 1):                               # bigodes
            x1, y1 = ex(25.5 + d * 1.2, s_ * 6.0); x2, y2 = ex(25.0 + d * 2.2, s_ * 10.2)
            t = np.clip(((X - x1) * (x2 - x1) + (Y - y1) * (y2 - y1)) / ((x2 - x1) ** 2 + (y2 - y1) ** 2), 0, 1)
            rosto.append(np.sqrt((X - x1 - t * (x2 - x1)) ** 2 + (Y - y1 - t * (y2 - y1)) ** 2) - 0.45)
    for vv in (-7.8, 7.8):
        x0, y0 = ex(25.8, vv)
        boch.append(c2d(x0, y0, 1.8))
    for s_ in (-1, 1):                                  # dentro da orelha
        e = np.radians(s_ * 38)
        x0, y0 = ex(28 + 10.6 * np.cos(e), 10.6 * np.sin(e))
        boch.append(c2d(x0, y0, 1.7))
# corpo 3D com borda arredondada
rr = 2.2
q1 = forma + rr; q2 = np.abs(Z - H / 2) - H / 2 + rr
corpo = np.sqrt(np.maximum(q1, 0) ** 2 + np.maximum(q2, 0) ** 2) + np.minimum(np.maximum(q1, q2), 0) - rr
corpo = menos(corpo, cilindro(g, (0, 0, -1), FURO / 2, H + 2))
cara = np.minimum.reduce(rosto)
cara3 = np.maximum(cara, np.maximum(Z - H - 0.7, H - 0.5 - Z))
bo3 = np.maximum(np.minimum.reduce(boch), np.maximum(Z - H - 0.4, H - 0.5 - Z))
corpo = smin(corpo, cara3, 0.25)
corpo = smin(corpo, bo3, 0.25)
corpo = np.maximum(corpo, -Z)
# rolamento (só para a foto) e tampinhas
rol = np.maximum(cilindro(g, (0, 0, 0.3), FURO / 2 - 0.05, 7.0, 0.4), -cilindro(g, (0, 0, -1), 4.2, 10))
tampa = cilindro(g, (0, 0, H - 0.3), 10.5, 1.8, 0.8)
estrela = None
r_ = np.sqrt(X * X + Y * Y); a_ = np.arctan2(Y, X)
kk = np.cos(np.pi / 5) / np.cos((a_ + np.pi / 2) % (2 * np.pi / 5) - np.pi / 5)
estrela = np.maximum(r_ - 5.2 * (0.45 + 0.55 * np.clip((kk - np.cos(np.pi / 5)) / (1 - np.cos(np.pi / 5)), 0, 1) ** 2.5), np.maximum(H + 1.4 - Z, Z - H - 2.2))
tampa = smin(tampa, estrela, 0.3)
tampa = smin(tampa, cilindro(g, (0, 0, H - 4.0), 3.9, 4.2, 0.3), 0.4)        # pino que entra no furo de 8 mm do rolamento
pecas = {"c1": np.maximum(corpo, -cara3 + 0.0 * 0) , }
cor2 = np.maximum(cara, -corpo - 0.0)
partes = dividir(corpo, {"c2": np.maximum(cara, H - 0.3 - Z), "c4": np.maximum(np.minimum.reduce(boch), H - 0.3 - Z)})
m_t = malha(g, tampa); m_t.export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "spinner_tampa.stl"))
partes["c3"] = rol
partes_imp = {k: v for k, v in partes.items()}
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
for k, v_ in exportar(g, partes, os.path.join(d, "spinner"), faces=None).items():
    print(k, v_)
