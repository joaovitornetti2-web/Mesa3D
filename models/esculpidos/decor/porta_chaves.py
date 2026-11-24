"""Porta-Chaves Mímico – um baú mímico de parede: as chaves ficam penduradas nos dentões de baixo.
Tampa abaulada com veio de madeira, faixas de metal com rebites, cantoneiras, dois olhos espertos,
dentinhos de cima e fechadura. Modelado deitado de costas (posição de impressão): Z = para fora da parede, Y = para cima.
c1 madeira · c2 metal (faixas, rebites, cantoneiras, dentes, olhos e fechadura)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
g = Grade((-88, -44, 0), (88, 48, 40), passo)
X, Y, Z = g.x, g.y, g.z
W, BOCA = 80.0, 2.0

def circ(x, y, r):
    return np.sqrt((X - x) ** 2 + (Y - y) ** 2) - r
def ret(x, y, hx, hy, r=1.0):
    qx, qy = np.abs(X - x) - hx + r, np.abs(Y - y) - hy + r
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r

base = caixa(g, (0, -19, 6.5), (W, 21, 6.5), 3.0)
tampa = np.maximum(elipsoide(g, (0, BOCA, 0), (W, 40, 18)), np.maximum(BOCA - Y, -Z))
tampa = smax(tampa, Y - 38, 3)
madeira = smin(base, np.maximum(tampa, -Z), 1.2)
# veio de madeira
veio = np.abs(np.sin((Y + 1.5 * np.sin(X * 0.07) + 0.7 * np.sin(X * 0.19 + 1)) * 0.85))
madeira = madeira + 0.22 * np.clip(0.18 - veio, 0, 1) / 0.18
madeira = madeira + 0.03 * ruido(g, 1.5, 4)
# boca escura entre base e tampa
boca = caixa(g, (0, BOCA - 1.0, 9), (W - 9, 2.6, 12), 2.0)
madeira = menos(madeira, boca, 0.8)

relevo = lambda mask, h: np.maximum(mask, madeira - h)      # chapa que acompanha a superfície
metal_masks = []
# faixas verticais e rebites
faixas = None
for x0 in (-W + 20, W - 20):
    m = np.maximum(np.abs(X - x0) - 5.5, np.maximum(-38 - Y, Y - 37))
    faixas = m if faixas is None else np.minimum(faixas, m)
corpo = smin(madeira, relevo(faixas, 0.9), 0.3)
rebites = None
for x0 in (-W + 20, W - 20):
    for yy in (-34, -14, 14, 28):
        r_ = circ(x0, yy, 1.7)
        rebites = r_ if rebites is None else np.minimum(rebites, r_)
corpo = smin(corpo, relevo(rebites, 1.9), 0.4)
# cantoneiras
cant = np.minimum.reduce([ret(sx * (W + 2), sy, 16, 8, 2) for sx in (-1, 1) for sy in (-34, -4, 26)])
corpo = smin(corpo, relevo(cant, 1.1), 0.3)
# olhos: bolota de madeira, aro e pupila de metal (pupila olhando para o lado)
olhos_m = None
for s, rr in ((-1, 7.0), (1, 6.0)):
    cx, cy = s * 26, 21
    corpo = smin(corpo, relevo(circ(cx, cy, rr + 1.8), 3.2), 1.2)
    anel = np.maximum(circ(cx, cy, rr + 1.8), -circ(cx, cy, rr))
    pup = circ(cx + 2.0, cy - 1.0, rr * 0.45)
    m = np.minimum(anel, pup)
    olhos_m = m if olhos_m is None else np.minimum(olhos_m, m)
# sobrancelhas de metal (uma levantada)
sob = np.minimum(np.maximum(np.abs((Y - 32) + 0.25 * (X + 26)) - 1.2, np.abs(X + 26) - 8),
                 np.maximum(np.abs((Y - 31) - 0.1 * (X - 26)) - 1.2, np.abs(X - 26) - 7))
corpo = smin(corpo, relevo(sob, 1.6), 0.4)
# fechadura
fech = ret(0, -21, 7, 9, 2.5)
corpo = smin(corpo, relevo(fech, 1.2), 0.3)
buraco = np.minimum(cilindro(g, (0, -18.5, 0), 2.4, 30), caixa(g, (0, -23.5, 15), (1.1, 3.5, 15), 0.5))
corpo = menos(corpo, np.maximum(buraco, 10.5 - Z), 0.2)

# dentinhos de cima (dentro da boca, descendo da tampa)
dentes = None
for x in np.linspace(-W + 14, W - 14, 11):
    d = capsula(g, (x, BOCA + 1.6, 8.5), (x, BOCA - 2.8, 9.5), 2.5, 0.6)
    dentes = d if dentes is None else np.minimum(dentes, d)
corpo = smin(corpo, dentes, 0.5)
# dentões-gancho embaixo (é aqui que penduram as chaves)
ganchos = None
for x in (-45, -15, 15, 45):
    h = tubo(g, [(x, BOCA - 7.5, 10), (x, BOCA - 7.0, 19), (x, BOCA - 4.5, 25), (x, BOCA + 0.5, 27)], [3.6, 3.2, 2.7, 2.2])
    ganchos = h if ganchos is None else np.minimum(ganchos, h)
corpo = smin(corpo, ganchos, 0.8)
# furos escareados para parafuso
for x in (-W + 34, W - 34):
    corpo = menos(corpo, np.minimum(cilindro(g, (x, -33, -1), 2.1, 20), cilindro(g, (x, -33, 10.8), 4.4, 10)), 0.2)
corpo = np.maximum(corpo, -Z)
corpo = np.maximum(corpo, ret(0, -3, W + 4, 44, 4))       # apara rebarbas fora do contorno

pele = lambda mask, d=1.2: np.maximum(mask, -(corpo + d))   # cor só na casquinha de fora
cor2 = np.minimum.reduce([pele(faixas, 1.4), pele(rebites, 2.4), pele(cant, 3.0), pele(olhos_m, 1.0), pele(sob, 2.0),
                          pele(fech, 1.6), dentes - 0.3, ganchos - 0.4])
cor2 = np.maximum(cor2, -(corpo + 4.0))
for k, v in exportar(g, dividir(corpo, {"c2": cor2}), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "porta_chaves"), faces=None).items():
    print(k, v)
