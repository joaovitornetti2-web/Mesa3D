"""Caveira Porta-Dados – crânio estilizado oco que guarda dados; o topo da cabeça é a tampa. Um anel no corpo
entra por dentro da tampa (folga 0,25 mm). Velas derretidas em cima, cera escorrendo pela testa, rachadura e um
símbolo de ritual gravado. Cerca de 70 × 80 × 100 mm (com as velas).
Cores: c1 osso, c2 fundo das órbitas e do nariz, c3 velas e cera, c4 chamas.
Impressão (--imprimir): corpo e tampa em pé, lado a lado; suporte em árvore só sob o queixo e as órbitas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.15)
CORTE, E, F = 46.0, 2.6, 0.25
C0, R0 = (0, 2, 46), (31, 35, 31)
MN, MX = (-40, -46, 0), (130 if IMP else 40, 40, 112)


def campo(g):


    def cranio(g):
        X, Y, Z = g.x, g.y, g.z
        cab = elipsoide(g, C0, R0)
        cab = smin(cab, elipsoide(g, (0, -14, 30), (27, 22, 20)), 6)
        mand = smin(elipsoide(g, (0, -20, 12), (21, 17, 12)), caixa(g, (0, -14, 8), (18, 15, 8), 6), 4)
        cab = smin(cab, mand, 6)
        cab = smax(cab, -Z, 2)
        for sx in (-1, 1):
            cab = smin(cab, elipsoide(g, (sx * 21, -22, 28), (7, 8, 6)), 4)        # maçãs do rosto
            cab = menos(cab, elipsoide(g, (sx * 32.5, -2, 34), (3.2, 11, 8)), 3)     # têmporas (rasas)
        cab = cab + ruido(g, 2.0, 21) * 0.15 + 0.07 * ruido(g, 0.5, 22) + 0.06 * np.clip(ruido(g, 0.35, 23) - 1.2, 0, None)   # osso poroso
        # suturas do crânio (linha em zigue-zague no alto e atrás)
        sut = np.abs(X - 1.2 * np.sin(Y * 1.6) - 0.6 * np.sin(Y * 4.1)) - 0.35
        sut2 = np.abs((Z - 52) + 0.15 * Y - 1.0 * np.sin(X * 1.5)) - 0.35
        cab = menos(cab, np.maximum(np.minimum(np.maximum(sut, Y + 18), np.maximum(sut2, -Y - 4)), -(cab + 0.9)), 0.15)
        orb = None
        for sx in (-1, 1):
            o = elipsoide(Vista(g, (sx * 12, -33, 38), rot_y(sx * 12)), (sx * 12, -33, 38), (8.2, 9, 9.5))
            orb = o if orb is None else np.minimum(orb, o)
        furos = np.minimum(orb, elipsoide(g, (0, -37, 25), (4, 6, 6.5)))
        cab = menos(cab, furos, 1.2)
        escuro = furos - 1.6
        dentes = None
        for i in range(-3, 4):
            d = caixa(g, (i * 4.6, -33.5 + abs(i) * 0.9, 14), (2.0, 2.5, 3.6), 1.0)
            dentes = d if dentes is None else np.minimum(dentes, d)
        cab = menos(cab, np.maximum(caixa(g, (0, -34, 14), (17, 5, 4.6), 1.5), -dentes + 0.35), 0.3)
        # rachadura e símbolo gravado na testa (círculo com triângulo vazado)
        rach = tubo(g, [(14, -26, 62), (17, -24, 56), (15, -27, 51), (19, -25, 46)], [0.7, 0.6, 0.5, 0.3])
        cab = menos(cab, np.maximum(rach, -(cab + 2.0)), 0.2)
        u, w = X, Z - 58                                        # Marca de Sangue num círculo, gravada na testa
        simb = np.minimum(np.abs(np.sqrt(u ** 2 + w ** 2) - 8) - 0.6, sigilo_sangue(u, w, 12.0, 1.3))
        cab = menos(cab, np.maximum(simb, np.maximum(-(Y + 20), -(cab + 1.0))), 0.2)
        # oco
        oco = smin(elipsoide(g, C0, (R0[0] - E, R0[1] - E, R0[2] - E)), elipsoide(g, (0, -12, 26), (22, 18, 14)), 5)
        cab = menos(cab, np.maximum(oco, 4 - Z))
        cab = np.minimum(cab, np.maximum(np.maximum(furos - 1.8, -furos), oco))   # fundo das órbitas fechado por dentro
        # velas em cima e cera escorrendo
        velas = chamas = None
        for (x, y, h, r) in [(-9, 6, 22, 4.2), (6, 12, 15, 3.6), (12, -4, 10, 3.2)]:
            z0 = 74.0
            v = smin(cilindro(g, (x, y, z0 - 4), r, h + 4, 1.0), cilindro(g, (x, y, z0 - 4), r + 2.6, 2.6, 1.2), 1.5)
            for k in range(3):
                a = k * 2.1 + x
                p0 = (x + r * np.cos(a), y + r * np.sin(a), z0 + h - 1)
                v = smin(v, capsula(g, p0, (p0[0], p0[1], p0[2] - h * (0.4 + 0.2 * k)), 1.2, 1.5), 0.8)
            v = v + 0.12 * np.abs(np.sin(np.arctan2(Y - y, X - x) * 7 + Z * 0.5)) * np.clip(1 - np.abs(v) / 1.0, 0, 1)   # cera em camadas
            velas = v if velas is None else np.minimum(velas, v)
            ch = elipsoide(g, (x, y, z0 + h + 2.6), (1.7, 1.7, 2.2))
            for (dx, dy, hh, rr_) in [(0, 0, 7.5, 1.1), (0.8, 0.5, 5, 0.7), (-0.8, 0.4, 5.5, 0.7)]:
                ch = smin(ch, tubo(g, [(x + dx * 0.4, y + dy * 0.4, z0 + h + 2.5), (x + dx + 0.3, y + dy, z0 + h + 2.5 + hh * 0.6), (x + dx * 0.4 - 0.3, y + dy * 0.4, z0 + h + 2.5 + hh)], [rr_, rr_ * 0.6, 0.15]), 0.5)
            ch = smin(ch, capsula(g, (x, y, z0 + h - 0.5), (x, y, z0 + h + 2.0), 0.35), 0.2)                                    # pavio
            chamas = ch if chamas is None else np.minimum(chamas, ch)
        for (x, c) in [(-6, 14), (4, 20), (10, 9)]:
            velas = np.minimum(velas, capsula(g, (x, -26, 66), (x, -31.5, 66 - c), 2.0, 2.6))
        tudo = np.minimum.reduce([cab, velas, chamas])
        return tudo, escuro, velas, chamas


    def anel(g, folga=0.0):
        """anel de encaixe: sobe 3 mm acima do corte por dentro da tampa e se funde na parede do corpo embaixo."""
        Z = g.z
        fora = elipsoide(g, C0, (R0[0] - E - F + folga, R0[1] - E - F + folga, R0[2] - E - F + folga))
        dentro = elipsoide(g, C0, (R0[0] - E - 1.8, R0[1] - E - 1.8, R0[2] - E - 1.8))
        a = np.maximum(np.maximum(fora, -dentro), np.maximum(CORTE - 4 - Z, Z - CORTE - 3 - folga))
        return a


    tudo, escuro, claro, chamas = cranio(g)
    Z = g.z
    corpo = np.minimum(np.maximum(tudo, Z - CORTE), anel(g))
    if IMP:
        gv = Vista(g, (0, 0, 0), np.eye(3))
        gv.x, gv.z = gv.x - 90, gv.z + CORTE + 0.3          # tampa ao lado, base do corte na mesa
        t2, e2, c2, ch2 = cranio(gv)
        tampa = menos(np.maximum(t2, CORTE + 0.3 - gv.z), anel(gv, F))
        escuro, claro, chamas = np.minimum(escuro, e2), np.minimum(claro, c2), np.minimum(chamas, ch2)
    else:
        tampa = menos(np.maximum(tudo, CORTE + 0.3 - Z), anel(g, F))
    tudo = np.maximum(np.minimum(corpo, tampa), -Z)
    return tudo, {"c4": chamas, "c3": claro, "c2": escuro}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "caveira", IMP)).items():
        print(k, v)
