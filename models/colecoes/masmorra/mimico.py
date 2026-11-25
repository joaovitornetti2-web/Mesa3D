"""Mímico Porta-Dados – baú de madeira com cintas de metal que na verdade é um monstro (criatura do SRD 5.1).
Base oca guarda os dados; a tampa abaulada é peça separada, apoia num rebaixo e tem dentes que se intercalam
com os da base. Língua vermelha sai da caixa e pende pela frente; dois olhos saltados na tampa.
Cores: c1 madeira, c2 cintas/rebites/pupilas, c3 dentes e olhos, c4 língua.
Foto: tampa entreaberta. Impressão (--imprimir): base em pé e tampa de boca para cima, lado a lado, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
L, P, HB = 72.0, 54.0, 34.0          # largura, profundidade, altura da base
HT = 20.0                            # altura da tampa (arco)
E = 2.4                              # parede
ABRE = 38                           # ângulo de abertura na foto

if IMP:
    g = Grade((-40, -32, 0), (122, 32, HB + 8), passo)
else:
    g = Grade((-42, -50, 0), (42, 40, 88), passo)
X, Y, Z = g.x, g.y, g.z


def base_caixa(g):
    X, Y, Z = g.x, g.y, g.z
    corpo = caixa(g, (0, 0, HB / 2), (L / 2, P / 2, HB / 2), 2.0)
    # tábuas: sulcos horizontais nas laterais
    for zz in (9, 17.5, 26):
        corpo = menos(corpo, np.maximum(np.abs(Z - zz) - 0.5, -(np.maximum(np.abs(X) - L / 2 + 0.7, np.abs(Y) - P / 2 + 0.7))), 0.3)
    # pezinhos
    for sx in (-1, 1):
        for sy in (-1, 1):
            corpo = smin(corpo, np.maximum(esfera(g, (sx * (L / 2 - 4), sy * (P / 2 - 4), 2.5), 5.5), -Z), 1)
    oco = caixa(g, (0, 0, HB / 2 + E + 1), (L / 2 - E, P / 2 - E, HB / 2), 1.2)
    corpo = menos(corpo, oco)
    # cintas de metal (relevo) e rebites
    cinta = np.maximum(np.abs(np.abs(X) - 22) - 3.2, np.maximum(caixa(g, (0, 0, HB / 2), (L / 2 + 0.9, P / 2 + 0.9, HB / 2 - 0.01), 2.4), -caixa(g, (0, 0, HB / 2), (L / 2 - 0.6, P / 2 - 0.6, HB), 1.5)))
    rebite = None
    for sx in (-22, 22):
        for zz in (6, 30):
            for sy in (-1, 1):
                r = esfera(g, (sx, sy * (P / 2 + 0.9), zz), 1.4)
                rebite = r if rebite is None else np.minimum(rebite, r)
    metal = np.minimum(cinta, rebite)
    # fechadura na frente
    fech = caixa(g, (0, -P / 2 - 0.6, HB - 7), (5, 1.6, 6), 1.0)
    metal = np.minimum(metal, fech)
    corpo = np.minimum(corpo, metal)
    corpo = menos(corpo, caixa(g, (0, -P / 2 - 2.5, HB - 8), (1.0, 2, 2.4), 0.5))  # buraco da chave
    # dentes na borda de cima (frente e laterais), para cima
    dentes = None
    for i, xx in enumerate(np.arange(-30, 31, 7.5)):
        t = capsula(g, (xx, -P / 2 + E / 2 + 0.6, HB - 1), (xx, -P / 2 + E / 2 + 1.4, HB + 5.5 + (i % 2)), 2.3, 0.35)
        dentes = t if dentes is None else np.minimum(dentes, t)
    for sx in (-1, 1):
        for yy in (-14, 0, 14):
            t = capsula(g, (sx * (L / 2 - E / 2 - 0.6), yy, HB - 1), (sx * (L / 2 - E / 2 - 1.4), yy, HB + 5), 2.1, 0.35)
            dentes = np.minimum(dentes, t)
    # língua: deitada no fundo, sobe e pende pela frente
    lingua = tubo(g, [(6, 10, E + 2), (2, 0, E + 4), (-3, -12, HB - 6), (-5, -P / 2 + 1, HB + 2.5), (-6, -P / 2 - 4, HB - 4), (-4, -P / 2 - 6, HB - 13)],
                  [6.5, 6.5, 6, 5.5, 5, 3.8])
    lingua = np.maximum(lingua, np.abs(Z - lingua_z(g)) - 100)
    lingua = menos(lingua, np.maximum(np.abs(X + 3) - 0.6, np.abs(Y + 6) - 30), 0.4)  # sulco do meio
    lingua = np.maximum(lingua, -Z + E)
    tudo = smin(np.minimum(corpo, dentes), lingua, 1.0)
    return tudo, metal, dentes, lingua


def lingua_z(g):
    return g.z  # sem achatamento extra


def tampa(g):
    """tampa no próprio referencial: borda em z = HB, arco até HB + HT; dobradiça em y = +P/2."""
    X, Y, Z = g.x, g.y, g.z
    R = (HT ** 2 + (P / 2) ** 2) / (2 * HT)
    arco = np.sqrt((Y) ** 2 + (Z - (HB + HT - R)) ** 2) - R
    corpo = np.maximum(arco, np.maximum(np.abs(X) - L / 2, HB - Z))
    corpo = smax(corpo, caixa(g, (0, 0, HB + HT / 2), (L / 2, P / 2, HT / 2 + 0.01), 0), 1.5)
    oco = np.maximum(arco + E, np.maximum(np.abs(X) - L / 2 + E, HB - 1 - Z))
    corpo = menos(corpo, oco)
    # tábuas curvas
    for yy in (-12, 0, 12):
        corpo = menos(corpo, np.maximum(np.abs(Y - yy) - 0.5, -(arco + 0.7)), 0.3)
    # lábio que encaixa por dentro da base
    labio = np.maximum(caixa(g, (0, 0, HB - 1.5), (L / 2 - E - 0.25, P / 2 - E - 0.25, 1.5), 1.0), -caixa(g, (0, 0, HB - 1.5), (L / 2 - 2 * E, P / 2 - 2 * E, 3), 0.8))
    labio = np.maximum(labio, -np.maximum(np.abs(Y + P / 2 - E - 2) - 3, np.abs(X) - 33))  # aberto na frente (dentes)
    corpo = np.minimum(corpo, labio)
    # cintas curvas e borda de metal
    cinta = np.maximum(np.abs(np.abs(X) - 22) - 3.2, np.maximum(arco - 0.9, -(arco + 0.6)))
    cinta = np.maximum(cinta, HB - Z)
    borda = np.maximum(np.maximum(arco - 0.9, -(arco + 0.6)), np.maximum(np.abs(np.abs(X) - L / 2 + 1.4) - 1.6, HB - Z))
    metal = np.minimum(cinta, borda)
    corpo = np.minimum(corpo, metal)
    # dentes para baixo, intercalados com os da base
    dentes = None
    for i, xx in enumerate(np.arange(-26.25, 27, 7.5)):
        t = capsula(g, (xx, -P / 2 + E / 2 + 0.6, HB + 1), (xx, -P / 2 + E / 2 + 1.4, HB - 5 - (i % 2)), 2.3, 0.35)
        dentes = t if dentes is None else np.minimum(dentes, t)
    for sx in (-1, 1):
        for yy in (-7, 7):
            dentes = np.minimum(dentes, capsula(g, (sx * (L / 2 - E / 2 - 0.6), yy, HB + 1), (sx * (L / 2 - E / 2 - 1.4), yy, HB - 4.5), 2.1, 0.35))
    # olhos saltados na frente da tampa
    olho, pupila = None, None
    for sx in (-1, 1):
        c = (sx * 13, -P / 2 + 6, HB + 10)
        o = esfera(g, c, 6.2)
        pp = esfera(g, (sx * 12.2, -P / 2 + 1.2, HB + 9.4), 2.9)
        olho = o if olho is None else np.minimum(olho, o)
        pupila = pp if pupila is None else np.minimum(pupila, pp)
        # pálpebra (sobrancelha brava)
        corpo = smin(corpo, capsula(g, (sx * 20, -17.0, HB + 14.5), (sx * 7, -13.0, HB + 17.0), 2.2, 1.6), 1.2)
    pupila = np.maximum(pupila, olho - 0.01 + 0.0) if False else np.maximum(pupila, olho + 0.0)
    tudo = smin(np.minimum(corpo, dentes), olho, 1.2)
    return tudo, metal, dentes, olho, pupila


b_tudo, b_metal, b_dentes, b_lingua = base_caixa(g)
if IMP:
    # tampa de boca para cima ao lado: gira 180° no eixo x e translada
    gv = Vista(g, (82, 0, 0), rot_x(180))
    gv.z = gv.z + HB + HT          # leva a borda (z = HB) para a mesa
    gv.x = gv.x - 82
else:
    gv = Vista(g, (0, P / 2, HB), rot_x(-ABRE))
t_tudo, t_metal, t_dentes, t_olho, t_pupila = tampa(gv)
tudo = np.minimum(b_tudo, t_tudo)
metal = np.minimum(b_metal, np.minimum(t_metal, t_pupila))
claro = np.minimum(b_dentes, np.minimum(t_dentes, t_olho))
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": b_lingua, "c2": metal, "c3": claro})
for k, v in exportar(g, partes, saida(__file__, "mimico", IMP), faces=None).items():
    print(k, v)
