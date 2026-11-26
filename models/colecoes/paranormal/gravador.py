"""Gravador da Investigação – gravador de fita portátil antigo que guarda cartas: fenda no topo para cartas de
RPG/baralho (até 66 × 92 mm, ~30 cartas com capa), janela com a fita cassete e os carretéis, grade do alto-falante,
teclas (a de gravar em vermelho) e alça. 112 × 44 × 76 mm.
Cores: c1 carcaça, c2 grade, teclas e janela, c3 etiqueta e carretéis, c4 tecla de gravar e luz.
Em pé, sem suporte (alça com arco de 45°)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
LX, LY, H = 56.0, 22.0, 62.0
MN, MX = (-60, -26, 0), (60, 26, 80)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    corpo = caixa(g, (0, 0, H / 2), (LX, LY, H / 2), 6)
    # fenda das cartas (no topo, ao longo de x)
    corpo = menos(corpo, caixa(g, (0, 4, H - 22), (47, 4.2, 30), 1.5))
    # frente (y negativo): janela da fita à esquerda, grade à direita, teclas em cima
    fr = -LY
    janela = caixa(g, (-22, fr, 34), (24, 2.4, 13), 3)
    corpo = menos(corpo, janela, 0.6)
    escuro = np.maximum(caixa(g, (-22, fr + 1.2, 34), (24.6, 2.0, 13.6), 3.2), -caixa(g, (-22, fr, 34), (22.4, 4, 11.4), 2.4))   # moldura
    # fita: etiqueta, carretéis com dentes
    fita = caixa(g, (-22, fr + 2.6, 34), (22, 0.8, 11), 2)
    etiq = caixa(g, (-22, fr + 1.6, 40), (18, 0.6, 3.6), 1.0)
    carr = None
    for xx in (-33, -11):
        rad = np.sqrt((X - xx) ** 2 + (Z - 32) ** 2)
        c = np.maximum(np.abs(rad - 5.2) - 1.1, np.abs(Y - fr - 1.8) - 0.8)
        a = np.arctan2(Z - 32, X - xx)
        dente = np.maximum(np.maximum(rad - 4.3, 2.6 - rad), np.maximum(np.abs(np.mod(a * 6 / (2 * np.pi), 1) - 0.5) - 0.18, np.abs(Y - fr - 1.8) - 0.8))
        c = np.minimum(c, dente)
        carr = c if carr is None else np.minimum(carr, c)
    claro = np.minimum(etiq, carr)
    # grade do alto-falante: furinhos em hexágono
    gx, gz = X - 30, Z - 32
    mx, mz = np.mod(gx + 2.5, 5.0) - 2.5, np.mod(gz + 2.165 + 2.165 * np.mod(np.floor((gx + 2.5) / 5), 2), 4.33) - 2.165
    furos = np.maximum(np.sqrt(mx ** 2 + mz ** 2) - 1.3, np.maximum(np.sqrt(gx ** 2 + gz ** 2) - 16, np.abs(Y - fr) - 1.6))
    corpo = menos(corpo, furos)
    grade = np.maximum(np.abs(np.sqrt(gx ** 2 + gz ** 2) - 17) - 1.0, np.abs(Y - fr - 0.2) - 0.9)
    escuro = np.minimum(escuro, grade)
    # teclas na frente, em cima
    teclas = vermelho = None
    for i, xx in enumerate(np.arange(-40, 1, 10)):
        t = caixa(g, (xx, fr - 1.0, 54), (4, 2.2, 3), 1.0)
        if i == 0:
            vermelho = t
        else:
            teclas = t if teclas is None else np.minimum(teclas, t)
    luz = esfera(g, (30, fr - 0.4, 54), 1.8)
    vermelho = np.minimum(vermelho, luz)
    escuro = np.minimum(escuro, teclas)
    # alça
    alca = toro(Vista(g, (0, 15, H - 14), rot_x(90)), (0, 15, H - 14), 30, 3.2, 1.0)
    alca = np.maximum(alca, -(Z - H + 2))
    alca = np.maximum(alca, np.abs(X) - 34)
    corpo = smin(corpo, alca, 2)
    corpo = menos(corpo, caixa(g, (0, 4, H - 22), (47, 4.2, 30), 1.5))   # fenda livre mesmo com a alça
    tudo = np.minimum.reduce([corpo, escuro, fita, claro, vermelho])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": vermelho, "c3": claro, "c2": np.minimum(escuro, fita)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "gravador", IMP)).items():
        print(k, v)
