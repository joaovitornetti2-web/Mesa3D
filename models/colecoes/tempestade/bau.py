"""Baú do Tesouro – porta-dados em forma de baú aberto: tampa abaulada fixa a 110° (imprime junto, sem suporte),
cintas de metal com rebites, fechadura, moedas empilhadas transbordando pela frente e uma gema no topo da pilha.
O espaço atrás da pilha guarda os dados. 86 × 78 × 82 mm.
Cores: c1 madeira, c2 metal, c3 gema, c4 moedas. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.13)
L, P, HB, E = 40.0, 27.0, 36.0, 2.6
MN, MX = (-46, -42, 0), (46, 62, 98)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 2.0, 111)
    caixa_b = caixa(g, (0, 0, HB / 2), (L, P, HB / 2), 2.0) + rr * 0.15
    for zz in (12, 24):
        caixa_b = menos(caixa_b, np.maximum(np.abs(Z - zz) - 0.5, -(np.maximum(np.abs(X) - L + 0.7, np.abs(Y) - P + 0.7))), 0.3)
    caixa_b = menos(caixa_b, caixa(g, (0, 0, HB / 2 + E + 1), (L - E, P - E, HB / 2), 1.2))
    # tampa abaulada aberta, presa na traseira (y = +P), girada 110°
    gv = Vista(g, (0, P, HB), rot_x(-110))
    R = (16 ** 2 + P ** 2) / (2 * 16)
    arc = np.sqrt(gv.y ** 2 + (gv.z - (HB + 16 - R)) ** 2) - R
    tampa = np.maximum(arc, np.maximum(np.abs(gv.x) - L, HB - gv.z))
    tampa = menos(tampa, np.maximum(arc + E, np.maximum(np.abs(gv.x) - L + E, HB - 1 - gv.z)))
    # metal: cintas verticais na caixa, curvas na tampa, fechadura, rebites
    cin = np.maximum(np.abs(np.abs(X) - 24) - 3.2, np.maximum(caixa(g, (0, 0, HB / 2), (L + 0.9, P + 0.9, HB / 2 - 0.01), 2.4), -caixa(g, (0, 0, HB / 2), (L - 0.6, P - 0.6, HB), 1.5)))
    cin_t = np.maximum(np.abs(np.abs(gv.x) - 24) - 3.2, np.maximum(np.maximum(arc - 0.9, -(arc + 0.6)), HB - gv.z))
    fech = caixa(g, (0, -P - 0.6, HB - 7), (5, 1.6, 6), 1.0)
    reb = None
    for sx in (-24, 24):
        for zz in (6, 30):
            for sy in (-1, 1):
                r = esfera(g, (sx, sy * (P + 0.9), zz), 1.4)
                reb = r if reb is None else np.minimum(reb, r)
    metal = np.minimum.reduce([cin, cin_t, fech, reb])
    corpo = np.minimum.reduce([caixa_b, tampa])
    corpo = menos(corpo, caixa(g, (0, -P - 2.5, HB - 8), (1.0, 2, 2.4), 0.5))
    # moedas: pilha no lado da frente, transbordando pela borda
    rng = np.random.default_rng(7)
    moedas = None
    for i in range(34):
        t = i / 33
        x = rng.uniform(-30, 30)
        y = rng.uniform(-P + 2, -4)
        z = HB - 6 + 10 * np.exp(-((x / 22) ** 2)) * (1 - (y + 4) / -26 * 0.4) + rng.uniform(-1, 1.5)
        ax, ay = rng.uniform(-35, 35), rng.uniform(-35, 35)
        vm = Vista(g, (x, y, z), mul(rot_x(ax), rot_y(ay)))
        m = cilindro(vm, (x, y, z - 0.9), 5.0, 1.8, 0.5)
        m = menos(m, np.maximum(np.sqrt((vm.x - x) ** 2 + (vm.y - y) ** 2) - 3.4, np.abs(vm.z - z - 0.9) - 0.3), 0.2)
        moedas = m if moedas is None else np.minimum(moedas, m)
    for (x, z, ax) in [(-14, 26, 80), (-8, 18, 75), (10, 30, 70), (16, 22, 85)]:            # moedas escorrendo pela frente
        vm = Vista(g, (x, -P - 1.5, z), rot_x(ax))
        m = cilindro(vm, (x, -P - 1.5, z - 0.9), 5.0, 1.8, 0.5)
        moedas = np.minimum(moedas, m)
    monte = np.maximum(elipsoide(g, (0, -14, HB - 8), (34, 13, 14)), -caixa(g, (0, 0, HB / 2), (L - 0.5, P - 0.5, HB), 1))   # recheio sob as moedas
    monte = np.maximum(monte, caixa(g, (0, 0, HB / 2 + 2), (L - E + 0.4, P - E + 0.4, HB / 2 + 4), 1.2))
    moedas = np.minimum(moedas, monte + 0.4)
    gema = np.maximum(np.abs(X) * 0.9 + np.abs(Y + 12) * 0.9 + np.abs(Z - HB - 9) - 5.2, -(Z - HB - 5.5))   # gema lapidada
    perto = np.clip(1 - np.abs(corpo) / 1.5, 0, 1)
    u = np.where(np.abs(X) / L > np.abs(Y) / P, Y, X)
    corpo = corpo + perto * (madeira(u, Z, tabua=9, fenda=0.5, prof=0.4, veio=0.12, semente=132) + desgaste(g, 0.25, 133))
    metal = metal + 0.05 * ruido(g, 0.5, 134)
    tudo = np.minimum.reduce([corpo, metal, moedas, gema])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": gema, "c4": moedas, "c2": metal}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "bau", IMP)).items():
        print(k, v)
