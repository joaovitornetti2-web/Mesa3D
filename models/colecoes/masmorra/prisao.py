"""Prisão de Dados – cela de masmorra para "prender" o dado que rolou mal. Paredes de pedra em blocos,
frente com grades de ferro e portinha com cadeado, tocha acesa na lateral e uma caveira no chão.
Aberta em cima: o dado entra por cima (cabe até 6 dados d20 de 22 mm).
Cores: c1 pedra, c2 ferro, c3 caveira, c4 chama. Imprime em pé, sem suporte (tocha em balanço curto, 45°)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
L, P, H, E = 70.0, 58.0, 52.0, 4.0
g = Grade((-46, -36, 0), (40, 36, 74), passo)
X, Y, Z = g.x, g.y, g.z


def blocos(u, z, alt=8.5, comp=15.0, larg=0.8):
    """sulcos de blocos de pedra (campo > 0 longe do sulco)."""
    fila = np.floor(z / alt)
    du = np.mod(u + (np.mod(fila, 2)) * comp / 2, comp)
    dz = np.mod(z, alt)
    return np.minimum(np.minimum(dz, alt - dz), np.minimum(du, comp - du)) - larg / 2


rr = ruido(g, 1.6, 7)
fora = caixa(g, (0, 0, H / 2), (L / 2, P / 2, H / 2), 1.5) + rr * 0.25
# ameias no topo
for i in range(-3, 4):
    for sy in (-1, 1):
        fora = np.minimum(fora, caixa(g, (i * 10, sy * (P / 2 - E / 2), H + 3), (3.2, E / 2, 3.5), 0.8))
for j in (-1, 0, 1):
    for sx in (-1, 1):
        fora = np.minimum(fora, caixa(g, (sx * (L / 2 - E / 2), j * 18, H + 3), (E / 2, 3.2, 3.5), 0.8))
# rodapé
fora = smin(fora, caixa(g, (0, 0, 3), (L / 2 + 1.5, P / 2 + 1.5, 3), 1.2), 0.8)
# sulcos de blocos nas quatro faces
u = np.where(np.abs(X) / (L / 2) > np.abs(Y) / (P / 2), Y, X)
sulco = blocos(u, Z - 6)
# aplica sulcos só na casca externa (0,7 mm de fundo)
sulco_v = np.maximum(np.maximum(-sulco, np.maximum(6.5 - Z, Z - H + 0.5)), -(fora + 0.7))
corpo = menos(fora, sulco_v)
# interior
oco = caixa(g, (0, 0, H / 2 + 3), (L / 2 - E, P / 2 - E, H / 2), 1.0)
corpo = menos(corpo, oco)
# janela gradeada na frente: vão em arco
W, ZB, ZT = 17.0, 8.0, 36.0
du = X
vao = np.minimum(np.maximum(np.abs(du) - W, np.maximum(ZB - Z, Z - ZT)), np.maximum(np.sqrt(du ** 2 + (Z - ZT) ** 2) - W, ZT - Z))
corpo = menos(corpo, np.maximum(vao, np.abs(Y + P / 2) - E - 1))
# grades: barras verticais + duas travessas + moldura de ferro
barras = None
for xx in np.arange(-13.5, 14, 4.5):
    b = capsula(g, (xx, -P / 2 + E / 2, ZB - 1), (xx, -P / 2 + E / 2, ZT + np.sqrt(max(W ** 2 - xx ** 2, 0)) + 1), 1.15)
    barras = b if barras is None else np.minimum(barras, b)
for zz in (17, 30):
    barras = np.minimum(barras, caixa(g, (0, -P / 2 + E / 2, zz), (W, 1.1, 1.0), 0.5))
moldura = np.maximum(np.maximum(vao - 1.6, -vao), np.abs(Y + P / 2 - 0.2) - 1.3)
ferro = np.minimum(np.maximum(barras, vao - 0.6), moldura)
# cadeado pendurado
cad = np.minimum(caixa(g, (6.75, -P / 2 - 1.2, 22), (3.0, 1.4, 3.5), 1.0), toro(Vista(g, (6.75, -P / 2 - 1.2, 26), rot_x(90)), (6.75, -P / 2 - 1.2, 26), 2.2, 0.7))
ferro = np.minimum(ferro, cad)
# tocha na lateral esquerda: suporte de ferro, cabo e chama
sup = np.minimum(caixa(g, (-L / 2 - 1, -8, 32), (1.2, 3.5, 6), 0.6), capsula(g, (-L / 2 - 1, -8, 30), (-L / 2 - 6, -8, 34), 1.2))
cabo = capsula(g, (-L / 2 - 5, -8, 28), (-L / 2 - 8.5, -8, 42), 1.8, 2.6)
taca = esfera(g, (-L / 2 - 8.6, -8, 43), 3.6)
taca = np.maximum(taca, Z - 44.5)
ferro = np.minimum(ferro, np.minimum(sup, taca))
ch = Vista(g, (-L / 2 - 8.8, -8, 44), rot_y(-12))
chama = smin(elipsoide(ch, (-L / 2 - 8.8, -8, 47), (3.8, 3.8, 5.5)), capsula(ch, (-L / 2 - 8.8, -8, 48), (-L / 2 - 9.6, -8, 55), 2.4, 0.4), 1.2)
chama = smin(chama, capsula(ch, (-L / 2 - 8.0, -6.5, 46), (-L / 2 - 6.5, -5.5, 51), 1.6, 0.3), 1.0)
# caveira no chão, encostada no fundo
cx, cy, cz = 14, 14, E + 7.5
cranio = smin(esfera(g, (cx, cy, cz + 1), 7.0), elipsoide(g, (cx, cy - 3.5, cz - 3.2), (4.6, 4, 3.6)), 2.0)
olhos = np.minimum(esfera(g, (cx - 2.8, cy - 6.6, cz), 2.1), esfera(g, (cx + 2.8, cy - 6.6, cz), 2.1))
nariz = esfera(g, (cx, cy - 7.4, cz - 2.6), 0.9)
cranio = menos(cranio, np.minimum(olhos, nariz), 0.3)
cranio = np.maximum(cranio, E - Z)
tudo = np.minimum.reduce([corpo, ferro, cabo, chama, cranio])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": chama, "c3": cranio, "c2": ferro})
for k, v in exportar(g, partes, saida(__file__, "prisao", IMP), faces=None).items():
    print(k, v)
