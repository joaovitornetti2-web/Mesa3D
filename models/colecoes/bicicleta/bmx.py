"""BMX da Turma – miniatura de decoração (110 mm de comprimento): bicicleta BMX dos anos 80 com rodas de
magnésio de 5 raios, quadro de tubos, guidão alto, banco, pedais e placa de número "85", sobre uma base de terra
com uma rampinha. Cores: c1 quadro, c2 pneus, banco e manoplas, c3 rodas, c4 placa de número e base.
Em pé, sem suporte (rodas apoiadas na base)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.2)
RR, ZR = 21.0, 25.0          # raio da roda (com pneu) e altura do eixo
XT, XD = -34.0, 34.0         # eixo traseiro e dianteiro
g = Grade((-62, -22, 0), (62, 22, 92), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 1.6, 181)
# base de terra com rampinha
base = np.maximum(caixa(g, (0, 0, 2), (58, 18, 2), 3) + rr * 0.3, -Z)
rampa = np.maximum(np.maximum(np.abs(Y) - 15, np.abs(X - 46) - 12), (Z - 4) - (X - 34) * 0.35)
base = smin(base, np.maximum(rampa, -Z), 1.5)


def roda(cx):
    rad = np.sqrt((X - cx) ** 2 + (Z - ZR) ** 2)
    a = np.arctan2(Z - ZR, X - cx)
    pneu = np.sqrt((rad - RR + 2.6) ** 2 + Y ** 2) - 2.8
    pneu = pneu + np.float32(0.3) * ((np.cos(a * 60) > 0.3) & (rad > RR - 1))   # cravos do pneu
    aro = np.maximum(np.abs(rad - RR + 6) - 1.4, np.abs(Y) - 2.2)
    raios = np.maximum(np.maximum(np.abs(rad * np.sin((np.mod(a + np.pi / 5, 2 * np.pi / 5) - np.pi / 5))) - 1.6, rad - RR + 6), np.abs(Y) - 1.4)
    cubo = np.maximum(rad - 4.0, np.abs(Y) - 4.5)
    return pneu, np.minimum.reduce([aro, raios, cubo])


p1, r1 = roda(XT)
p2, r2 = roda(XD)
pneus, rodas = np.minimum(p1, p2), np.minimum(r1, r2)
# quadro (tubos)
pedal_c = (-4, 0, 24)
selim_c = (-14, 0, 52)
guidao_c = (26, 0, 54)
q = np.minimum.reduce([
    capsula(g, pedal_c, (XT, 0, ZR), 1.8),                    # corrente inferior
    capsula(g, selim_c, (XT, 0, ZR), 1.6),                    # garfo traseiro superior
    capsula(g, pedal_c, selim_c, 2.0),                        # tubo do selim
    capsula(g, pedal_c, (22, 0, 46), 2.2),                    # tubo inferior
    capsula(g, (-12, 0, 47), (22, 0, 48), 2.0),               # tubo superior
    capsula(g, (22, 0, 44), (24, 0, 52), 2.4),                # caixa de direção
])
for s in (-1, 1):
    q = np.minimum(q, capsula(g, (23, s * 3.2, 46), (XD, s * 3.2, ZR), 1.5))            # garfo dianteiro
    q = np.minimum(q, capsula(g, (XT, s * 3.2, ZR), (-4, s * 3.2, 24), 1.2))
# guidão alto em U
gu = np.minimum.reduce([capsula(g, (24, 0, 52), guidao_c, 1.6), capsula(g, (guidao_c[0], -14, 60), (guidao_c[0], 14, 60), 1.4),
                        capsula(g, (guidao_c[0], -14, 60), (guidao_c[0] - 2, -14, 54), 1.4), capsula(g, (guidao_c[0], 14, 60), (guidao_c[0] - 2, 14, 54), 1.4),
                        capsula(g, (guidao_c[0] - 2, -9, 54), (guidao_c[0] - 2, 9, 54), 1.4)])
manoplas = np.minimum(capsula(g, (guidao_c[0], -20, 60), (guidao_c[0], -14, 60), 2.0), capsula(g, (guidao_c[0], 14, 60), (guidao_c[0], 20, 60), 2.0))
q = np.minimum(q, gu)
# banco
banco = smin(elipsoide(g, (-15, 0, 56), (8, 4.2, 2.2)), capsula(g, selim_c, (-15, 0, 55), 1.6), 0.8)
# pedivela e pedais
coroa = np.maximum(np.sqrt((X - pedal_c[0]) ** 2 + (Z - pedal_c[2]) ** 2) - 6.5, np.abs(Y - 3.5) - 1.0)
ped = np.minimum.reduce([capsula(g, (pedal_c[0], 4.5, pedal_c[2]), (pedal_c[0] + 8, 4.5, pedal_c[2] - 8), 1.3),
                         caixa(g, (pedal_c[0] + 8, 8, pedal_c[2] - 8), (3, 3.5, 1), 0.5),
                         capsula(g, (pedal_c[0], -4.5, pedal_c[2]), (pedal_c[0] - 8, -4.5, pedal_c[2] + 8), 1.3),
                         caixa(g, (pedal_c[0] - 8, -8, pedal_c[2] + 8), (3, 3.5, 1), 0.5)])
q = np.minimum.reduce([q, coroa, ped])
# placa de número no guidão
placa = caixa(g, (guidao_c[0] + 4, 0, 53), (1.0, 9, 7), 2.5)
num = np.maximum(texto2d(-Y, Z - 53, "85", 8, "redonda"), np.abs(X - guidao_c[0] - 5.4) - 0.5)
escuro = np.minimum.reduce([pneus, banco, manoplas, num])
c4 = np.minimum(placa, base)
tudo = np.minimum.reduce([base, pneus, rodas, q, banco, manoplas, placa, num])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c2": escuro, "c3": rodas, "c4": c4})
for k, vv in exportar(g, partes, saida(__file__, "bmx", IMP), faces=None).items():
    print(k, vv)
