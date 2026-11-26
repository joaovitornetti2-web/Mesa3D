"""Máscara do Ritual – máscara de parede (decoração): rosto liso e sereno, com olhos vazados, marcas de ritual
pintadas em relevo (arcos e pontos na testa e nas maçãs), rachaduras e lágrimas vermelhas escorrendo.
Atrás é plana, com furo de prego. 92 × 124 × 24 mm.
Cores: c1 máscara, c2 marcas e rachaduras, c4 lágrimas. Deitada de costas, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
MN, MX = (-50, -66, 0), (50, 66, 28)


def campo(g):
    X, Y, Z = g.x, g.y, g.z            # máscara deitada: rosto para +z, testa para +y
    rosto = elipsoide(g, (0, 4, 0), (44, 60, 22))
    rosto = smin(rosto, elipsoide(g, (0, -40, 0), (26, 24, 16)), 10)                 # queixo
    rosto = smin(rosto, elipsoide(g, (0, -6, 14), (5, 16, 9)), 4)                    # nariz
    for sx in (-1, 1):
        rosto = menos(rosto, elipsoide(g, (sx * 16, 12, 26), (13, 8, 9)), 6)        # cavidade dos olhos
        rosto = smin(rosto, elipsoide(g, (sx * 20, -14, 13), (11, 9, 7)), 6)        # maçãs
    rosto = menos(rosto, elipsoide(g, (0, -28, 20), (10, 2.2, 6)), 1.0)             # boca fechada
    rosto = np.maximum(rosto, -Z)
    oco = elipsoide(g, (0, 4, -2), (40, 56, 18))
    rosto = menos(rosto, oco, 2)
    # olhos vazados em amêndoa
    olhos = None
    for sx in (-1, 1):
        a = np.maximum(np.sqrt((X - sx * 16) ** 2 + (Y - 6) ** 2) - 9, np.sqrt((X - sx * 16) ** 2 + (Y - 18) ** 2) - 9)
        a = np.maximum(a, np.abs(Y - 12) - 5)
        olhos = a if olhos is None else np.minimum(olhos, a)
    rosto = menos(rosto, olhos, 0.6)
    # marcas de ritual (pintadas em relevo, 0,6 mm acima da superfície)
    u, v = X, Y
    marcas = np.minimum.reduce([
        np.maximum(np.abs(np.sqrt(u ** 2 + (v - 26) ** 2) - 12) - 0.9, -(v - 30)),            # arco na testa
        np.sqrt(u ** 2 + (v - 44) ** 2) - 2.2,                                             # ponto na testa
        np.maximum(np.abs(u) - 0.9, np.abs(v - 36) - 4),
    ])
    for sx in (-1, 1):
        marcas = np.minimum(marcas, np.maximum(np.abs(np.sqrt((u - sx * 20) ** 2 + (v + 8) ** 2) - 7) - 0.8, v + 8))   # arcos nas maçãs
        for k in range(3):
            marcas = np.minimum(marcas, np.sqrt((u - sx * (14 + k * 6)) ** 2 + (v + 20) ** 2) - 1.3)
    marcas = np.maximum(marcas, np.maximum(np.abs(rosto) - 0.6, 2 - oco))   # só na face de fora
    marcas = np.maximum(marcas, Z - 30)
    # rachaduras (sulcos) e lágrimas vermelhas descendo dos olhos
    rach = np.minimum(tubo(g, [(26, 40, 16), (22, 30, 19), (27, 22, 20), (24, 14, 20)], [0.7, 0.6, 0.5, 0.3]),
                      tubo(g, [(-30, -30, 14), (-24, -36, 13), (-27, -44, 11)], [0.6, 0.5, 0.3]))
    rosto = menos(rosto, rach, 0.2)
    lagr = None
    for sx, comp in ((-1, 26), (1, 18)):
        l = tubo(g, [(sx * 13, 4, 21), (sx * 13.5, 4 - comp * 0.5, 22), (sx * 12.5, 4 - comp, 20)], [1.6, 1.4, 1.9])
        l = np.maximum(l, -(rosto + 0.0) - 1.2)
        lagr = l if lagr is None else np.minimum(lagr, l)
    # furo de prego atrás (buraco de fechadura)
    prego = np.maximum(np.minimum(np.sqrt(X ** 2 + (Y - 40) ** 2) - 3.4, np.maximum(np.abs(X) - 1.6, np.abs(Y - 35) - 5)), Z - 5)
    rosto = menos(rosto, prego)
    # Marca de Sangue pintada em relevo na testa; porcelana com craquelado fino
    casca = np.maximum(rosto - 0.7, -rosto - 0.4)
    marcas = np.minimum(marcas, np.maximum(np.maximum(sigilo_sangue(X, Y - 34, 16, 1.6), casca), 12 - Z))
    rosto = rosto + 0.04 * ruido(g, 0.5, 65)
    crq = np.abs(ruido_cel(g, 6.0, 66)) - 0.04
    rosto = menos(rosto, np.maximum(crq, np.maximum(-(rosto + 0.35), 10 - Z)), 0.05)
    tudo = np.minimum.reduce([rosto, marcas, lagr])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": lagr, "c2": marcas}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "mascara", IMP)).items():
        print(k, v)
