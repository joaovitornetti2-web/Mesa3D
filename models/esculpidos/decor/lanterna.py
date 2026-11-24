"""Lanterna do Mestre – lanterna sextavada de casinha mal-assombrada para vela de LED.
Seis janelas em arco com lua, estrelas e um d20 vazados (a luz desenha na parede), pilares de canto,
telhado curvo com argola, base com pezinhos. Encaixa por cima da vela (fundo aberto, vela de LED de até 40 mm).
1 cor (c1)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
g = Grade((-50, -50, 0), (50, 50, 138), passo)
X, Y, Z = g.x, g.y, g.z
A = 37.0          # apótema (centro até o meio da parede)
H0, H1 = 10.0, 88.0
ang = np.arctan2(Y, X)
setor = np.round(ang / (np.pi / 3)) * (np.pi / 3)
n = X * np.cos(setor) + Y * np.sin(setor)          # distância "radial" até a parede daquele lado
u = -X * np.sin(setor) + Y * np.cos(setor)         # coordenada ao longo da parede
hexa = lambda a: n - a

corpo = np.maximum(hexa(A), np.maximum(H0 - Z, Z - H1))
# base em degraus com pezinhos
base = np.maximum(hexa(A + 4) + 0.0, Z - H0)
base = smin(base, np.maximum(hexa(A + 2), np.abs(Z - H0 - 1.5) - 1.5), 0.8)
corpo = smin(corpo, np.maximum(base, 3 - Z), 0.8)
for k in range(6):
    a = np.radians(k * 60 + 30)
    pe = esfera(g, ((A + 1.5) / np.cos(np.radians(30)) * np.cos(a) * 0.92, (A + 1.5) / np.cos(np.radians(30)) * np.sin(a) * 0.92, 3.5), 5.0)
    corpo = smin(corpo, np.maximum(pe, -Z), 1.0)
# cornija de cima
corpo = smin(corpo, np.maximum(hexa(A + 3.5), np.abs(Z - H1 - 2) - 2), 0.8)
# pilares arredondados nos cantos
for k in range(6):
    a = np.radians(k * 60 + 30)
    r = A / np.cos(np.radians(30))
    corpo = smin(corpo, capsula(g, (r * np.cos(a), r * np.sin(a), H0 + 2), (r * np.cos(a), r * np.sin(a), H1 - 1), 3.6), 1.0)
# telhado curvo (seis águas que se curvam para dentro) e argola
t = np.clip((Z - (H1 + 4)) / 34, 0, 1)
telhado = np.maximum(hexa((A + 6) * (1 - t) ** 1.35 + 1.5), np.maximum(H1 + 4 - Z, Z - (H1 + 38)))
telhado = smin(telhado, np.maximum(hexa(A + 6.5), np.abs(Z - H1 - 5) - 1.6), 0.8)
corpo = smin(corpo, telhado, 1.0)
corpo = smin(corpo, esfera(g, (0, 0, H1 + 38), 4.0), 2)
argola = toro(Vista(g, (0, 0, H1 + 46), rot_x(90)), (0, 0, H1 + 46), 7.0, 2.0)
corpo = smin(corpo, argola, 1.5)

# frisos em arco em volta de cada janela (relevo) e janelas vazadas
W, ZB, ZT = 13.0, 24.0, 70.0         # meia largura, base e início do arco da janela
def arco(du, folga=0.0):
    """janela em arco gótico (2D em u, z)."""
    w = W + folga
    reta = np.maximum(np.abs(du) - w, np.maximum(ZB - folga - Z, Z - ZT))
    pont = np.maximum(np.sqrt((np.abs(du) + w) ** 2 + (Z - ZT) ** 2) - 2 * w, ZT - Z)
    pont = np.maximum(pont, np.abs(du) - w)
    return np.minimum(reta, pont)
moldura = np.maximum(np.maximum(arco(u, 2.4), -arco(u, 0.0)), np.abs(n - A - 0.6) - 1.4)
corpo = smin(corpo, moldura, 0.5)
# desenho da janela: o que é vazado. Tudo entre a moldura e o desenho fica como grade fininha.
def estrela(cu, cz, r, ri=0.45):
    a = np.arctan2(Z - cz, u - cu) - np.pi / 2
    rr = np.sqrt((u - cu) ** 2 + (Z - cz) ** 2)
    k = np.cos(np.pi / 5) / np.cos((a % (2 * np.pi / 5)) - np.pi / 5)
    return rr - r * (ri + (1 - ri) * np.clip((k - np.cos(np.pi / 5)) / (1 - np.cos(np.pi / 5)), 0, 1) ** 3)
lua = np.maximum(np.sqrt((u + 1) ** 2 + (Z - 50) ** 2) - 8.5, -(np.sqrt((u + 4.5) ** 2 + (Z - 53) ** 2) - 7.5))
vazado = np.minimum.reduce([lua, estrela(6, 63, 4.2), estrela(-6, 70, 3.0), estrela(7, 38, 3.2), estrela(-7, 32, 2.6),
                            np.sqrt(u ** 2 + (Z - 78) ** 2) - 2.0])
corte = np.maximum(vazado, np.abs(n - A) - 6)
corpo = menos(corpo, corte, 0.3)
# oco por dentro (parede 2,4 mm) e fundo aberto para a vela
oco = np.maximum(hexa(A - 2.4), np.maximum(-1 - Z, Z - (H1 + 2)))
oco = np.minimum(oco, np.maximum(hexa((A + 6) * (1 - t) ** 1.35 - 1.0), np.maximum(H1 - Z, Z - (H1 + 30))))
corpo = menos(corpo, oco)
corpo = np.maximum(corpo, -Z)

for k, v in exportar(g, {"c1": corpo}, os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "lanterna"), faces=None).items():
    print(k, v)
