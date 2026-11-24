"""Porta-Copos – jogo com 4 (2 mandalas de pétalas, 2 ondas) + suporte. Desenho em relevo macio só no topo
(troca de cor nas últimas camadas: pouca purga). Arquivo de prova monta 3 porta-copos em leque e o suporte atrás.
c1 base · c2 desenho em relevo."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

IMPRIMIR = "--imprimir" in sys.argv
sys.argv = [a for a in sys.argv if a != "--imprimir"]
passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
D, E, REL = 96.0, 4.0, 0.9
g = Grade((-115, -70, 0), (115, 120, 70), passo)
X, Y, Z = g.x, g.y, g.z

def porta_copo(cx, cy, z0, ang, desenho):
    a = np.radians(ang)
    u = (X - cx) * np.cos(a) + (Y - cy) * np.sin(a)
    v = -(X - cx) * np.sin(a) + (Y - cy) * np.cos(a)
    r = np.sqrt(u * u + v * v)
    th = np.arctan2(v, u)
    zl = Z - z0
    base = np.maximum(r - D / 2, np.abs(zl - E / 2) - E / 2)
    base = np.maximum(base, -np.maximum(r - (D / 2 - 4.5), (E - 0.6) - zl))      # rebaixo para o desenho
    # arte 2D (negativo = tem relevo)
    aro = np.abs(r - (D / 2 - 2.6)) - 1.0
    if desenho == "mandala":
        p1 = r - (16 + 13 * np.abs(np.cos(4 * th)) ** 0.6)        # flor de 8 pétalas
        p1 = np.maximum(p1, -(r - (10 + 9 * np.abs(np.cos(4 * th + np.pi / 4)) ** 0.6)))
        miolo = r - 5.5
        anel_pet = np.maximum(np.abs(r - 38) - 3.4 * np.abs(np.cos(8 * th)) ** 0.5 - 0.3, -(r - 33))
        pontos = np.sqrt((r - 31.5) ** 2 + (r * (((th + np.pi / 8) % (np.pi / 4)) - np.pi / 8)) ** 2) - 1.4
        arte = np.minimum.reduce([p1, miolo, anel_pet, pontos])
    else:
        ondas = np.abs(np.sin((r + 1.8 * np.sin(5 * th)) * np.pi / 7.0)) * 3.5 - 1.1
        arte = np.maximum(ondas, r - (D / 2 - 5.5))
        arte = np.minimum(arte, r - 4)
    arte = np.minimum(arte, aro)
    relevo = np.maximum(arte, np.maximum(E - 0.6 - zl, zl - (E + REL)))
    peca = np.minimum(base, relevo)
    return peca, relevo

pecas, cor2 = [], []
for cx, cy, z0, ang, dz in ((-53, -20, 0, 0, "mandala"), (53, -20, 0, 30, "ondas")):
    p, r_ = porta_copo(cx, cy, z0, ang, dz)
    pecas.append(p); cor2.append(r_)

# suporte: copinho com frente aberta em arco, pezinhos e borda com friso
SC = (0, 75)
x, y = X - SC[0], Y - SC[1]
rs = np.sqrt(x * x + y * y)
ts = np.arctan2(y, x)
sup = np.maximum(rs - (D / 2 + 5) - 1.2 * np.cos(16 * ts) * np.clip((Z - 8) / 10, 0, 1), np.maximum(-Z, Z - (56 + 3.5 * np.cos(8 * ts))))
sup = menos(sup, np.maximum(rs - (D / 2 + 1), 3.0 - Z))
frente = np.maximum(np.maximum(np.abs(x) - 30, -(y + 5)), 24 - Z + 0 * x)
arco = np.maximum(np.sqrt(x * x + (Z - 24) ** 2) - 30, -(y + 5))
sup = menos(sup, np.minimum(np.maximum(np.maximum(np.abs(x) - 30, -(y + 5)), np.maximum(Z - 24, 7 - Z)), np.maximum(arco, 24 - Z)), 2.0)
for k in range(3):
    a = np.radians(k * 120 + 90)
    sup = smin(sup, np.maximum(esfera(g, (SC[0] + (D / 2 + 2) * np.cos(a), SC[1] + (D / 2 + 2) * np.sin(a), 2.5), 5), -Z), 1.5)
# dois porta-copos guardados no suporte (só para a foto)
for zz, ang, dz in (() if IMPRIMIR else ((3.0, 0, "ondas"), (7.0, 30, "mandala"))):
    p, r_ = porta_copo(SC[0], SC[1], zz, ang, dz)
    pecas.append(p); cor2.append(r_)
corpo = np.minimum.reduce(pecas + [sup])
corpo = np.maximum(corpo, -Z)
for k, v in exportar(g, dividir(corpo, {"c2": np.minimum.reduce(cor2) - 0.05}), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl_imprimir" if IMPRIMIR else "stl", "porta_copos"), faces=None).items():
    print(k, v)
