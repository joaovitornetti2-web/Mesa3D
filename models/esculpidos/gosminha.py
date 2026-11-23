"""Gosminha – slime gulosa que engoliu meio d6 (ele ficou preso na cabeça).
c1 corpo · c2 olhos/boca · c3 brilhos · c4 dado, língua, bochechas."""
import sys
from sdf import *
from rosto import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
g = Grade((-27, -26, 0), (27, 25, 42), passo)
X, Y, Z = g.x, g.y, g.z
th = np.arctan2(Y, X)
rho = np.sqrt(X * X + Y * Y)

# corpo de gota mole, mais largo embaixo, com ondulação de gelatina
R = 17.5 - 0.10 * (Z - 6) * np.clip(Z - 6, 0, None) * 0.05 + 0.6 * np.sin(3 * th + 0.4) * np.exp(-((Z - 8) / 6) ** 2)
corpo = elipsoide(g, (0, 0, 14.5), (18.5, 17.5, 15.5))
corpo = smin(corpo, elipsoide(g, (0, 0, 5), (21, 20, 6)), 5)
# poça com bordinha irregular
poca_r = 22.5 + 1.6 * np.sin(5 * th + 1) + 0.8 * np.sin(9 * th + 2.3)
poca = np.maximum(rho - poca_r, np.abs(Z - 1.1) - 1.1) - 0.3
corpo = smin(corpo, poca, 3)
# pingos escorrendo
for ang, z0, comp, r in ((200, 18, 12, 2.6), (325, 15, 9, 2.2), (95, 20, 14, 2.4), (25, 13, 7, 1.9)):
    a = np.radians(ang)
    def ponto(z):
        rr = 18.6 if z > 8 else 20.5
        return (rr * np.cos(a), rr * np.sin(a) * 0.95, z)
    corpo = smin(corpo, tubo(g, [ponto(z0), ponto(z0 - comp * 0.6), ponto(z0 - comp)], [r * 0.7, r * 0.95, r * 1.2]), 1.2)
# topete de gosma enrolado
corpo = smin(corpo, tubo(g, [(1, 1, 28.5), (2.5, 2, 32.5), (5.5, 2, 34), (6.5, 1, 31.5), (4.8, 0.5, 30.2)], [3.2, 2.4, 1.7, 1.1, 0.7]), 2.0)
# bolhas presas na gosma (algumas saltadas, outras furadinhas)
rng = np.random.default_rng(4)
for k in range(9):
    a, e = rng.uniform(0, 2 * np.pi), rng.uniform(-0.2, 0.9)
    if -np.pi * 0.75 < a < -np.pi * 0.25 and e > 0.1:
        continue                       # deixa o rosto limpo
    c = (19 * np.cos(e) * np.cos(a), 17.8 * np.cos(e) * np.sin(a), 14.5 + 15 * np.sin(e))
    b = esfera(g, c, rng.uniform(0.9, 1.7))
    corpo = smin(corpo, b, 0.4) if k % 2 else menos(corpo, b, 0.3)

corpo = corpo + 0.03 * ruido(g, 2.0, 5)

# rosto: olhos desiguais, sorriso enorme lambendo o canto
f = Rosto(g, 14.5, 17.6, 0.99)
f.olho(-6.8, 19.0, 4.0, 5.2, (0.4, 0.3))
f.olho(6.4, 18.4, 3.4, 4.4, (0.4, 0.3))
f.boca(0.4, 10.8, 6.0, 3.6, lingua=(3.2, 0.4))
f.bochecha(-12.8, 13.6, 2.8, 1.8)
f.bochecha(12.4, 13.4, 2.8, 1.8)
corpo = f.aplicar(corpo)

# d6 enfiado de lado na cabeça, com os pontinhos cavados
v = Vista(g, (-8.0, -1.5, 28.0), mul(rot_z(20), rot_x(18), rot_y(-28)))
dado = caixa(v, (-8.0, -1.5, 28.0), (4.6, 4.6, 4.6), 1.1)
pips = None
for (dx, dz) in ((0, 0), (-2.2, 2.2), (2.2, -2.2)):          # face de cima: 3
    p = esfera(v, (-8.0 + dx, -1.5 + dz, 28.0 + 4.9), 0.85)
    pips = p if pips is None else np.minimum(pips, p)
for (dx, dz) in ((-2.0, -2.0), (2.0, 2.0)):                   # face da frente: 2
    pips = np.minimum(pips, esfera(v, (-8.0 + dx, -1.5 - 4.9, 28.0 + dz), 0.85))
dado = menos(dado, pips, 0.15)
corpo = smin(corpo, dado, 1.2)
corpo = np.maximum(corpo, -Z)

reg = {"c3": juntar(f.c3), "c4": juntar([dado - 0.6] + f.c4), "c2": juntar(f.c2)}
for k, v_ in exportar(g, dividir(corpo, reg), "stl/gosminha", faces=300000).items():
    print(k, v_)
