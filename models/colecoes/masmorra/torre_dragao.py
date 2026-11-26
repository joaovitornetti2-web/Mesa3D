"""Torre do Dragão – torre de dados redonda de pedra com um dragão enrolado em espiral da base ao topo; a cabeça
apoia nas ameias, de boca aberta sobre a entrada. Por dentro, três rampas alternadas embaralham o dado, que sai pelo
portão em arco para a bandeja (peça separada, com rebaixo onde a torre assenta).
Torre: Ø 76 × 168 mm; bandeja 150 × 125 × 20 mm; dado máximo d20 de 26 mm.
Cores: c1 pedra, c2 dragão, c3 chifres, dentes, garras e olhos, c4 barriga e asas.
Impressão: torre em pé, suporte em árvore só sob a cabeça e as asas; bandeja deitada, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *
import trimesh

passo, IMP = args(0.2)
RE, RI, HT = 34.0, 29.5, 150.0         # raio externo, canal, altura do corpo
BY = 30.0                              # a torre fica em y = +BY na bandeja (fundo)
ZB = 4.0                               # torre apoiada no rebaixo da bandeja (z = 4 na foto)


def torre(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + Y ** 2)
    ang = np.arctan2(Y, X)
    corpo = np.maximum(rad - RE, np.maximum(-Z, Z - HT))
    # rodapé e cornija
    corpo = smin(corpo, np.maximum(rad - RE - 2.5, Z - 8), 1)
    corpo = smin(corpo, np.maximum(rad - RE - 3, np.abs(Z - HT + 3) - 3), 1)
    # ameias
    for k in range(10):
        a = k * 2 * np.pi / 10
        corpo = np.minimum(corpo, caixa(Vista(g, (0, 0, 0), rot_z(np.degrees(a))), ((RE + 0.5), 0, HT + 5), (3.6, 5.5, 5), 1.0))
    # blocos de pedra irregulares, lascados
    perto = np.clip(1 - np.abs(corpo) / 2.0, 0, 1)
    na_parede = (Z > 9) & (Z < HT - 6.5)
    corpo = corpo + perto * (np.where(na_parede, tijolos(ang * RE, Z - 8, larg=15, alt=8.5, junta=0.7, prof=0.8, semente=3, irregular=0.35), 0) + desgaste(g, 0.4, 4))
    # canal interno
    corpo = menos(corpo, np.maximum(rad - RI, -1 - Z))
    # rampas alternadas (inclinação 50°), da parede até passar do centro
    for (z0, s) in [(128, 1), (98, -1), (68, 1)]:
        plano = np.abs((Z - z0) - 1.19 * s * X) - 1.6
        rampa = np.maximum(plano, np.maximum(rad - RI - 0.5, -s * X - 9))
        corpo = np.minimum(corpo, rampa)
    # piso inclinado até o portão (frente, y negativo)
    piso = np.maximum((Z - 2) - 0.55 * (Y + RI), np.maximum(rad - RI - 0.5, -Z))
    corpo = np.minimum(corpo, piso)
    # portão em arco na frente
    W, ZT = 19.0, 26.0
    arco = np.minimum(np.maximum(np.abs(X) - W, np.maximum(-1 - Z, Z - ZT)), np.maximum(np.sqrt(X ** 2 + (Z - ZT) ** 2) - W, ZT - Z))
    corpo = menos(corpo, np.maximum(arco, Y + 10))
    corpo = smin(corpo, np.maximum(np.maximum(arco - 2.2, -arco), np.maximum(np.abs(Y + RE + 0.5) - 1.6, -Z)), 0.6)  # moldura
    # janelinhas
    for (a, z) in [(130, 60), (40, 100), (220, 115)]:
        v = Vista(g, (0, 0, 0), rot_z(a))
        jan = np.maximum(np.minimum(np.maximum(np.abs(v.y) - 3, np.abs(v.z - z) - 5), np.sqrt(v.y ** 2 + (v.z - z - 5) ** 2) - 3), -(v.x - RI + 1))
        corpo = menos(corpo, jan)

    # ---------------- dragão ----------------
    # corpo em espiral: começa na base atrás, dá ~1,25 volta subindo e termina com o pescoço sobre as ameias
    pts, raios = [], []
    N = 26
    for i in range(N):
        t = i / (N - 1)
        a = np.radians(110 + 450 * t)           # sobe girando no sentido anti-horário
        r = RE + 4.5 - 1.0 * t
        z = 6 + (HT - 6) * t ** 1.05
        pts.append((r * np.cos(a), r * np.sin(a), z))
        raios.append(4.0 + 5.5 * np.sin(np.pi * min(1, t * 1.25)) ** 0.7 if t < 0.95 else 6.5)
    raios[0] = 1.2
    dr = tubo(g, pts, raios)
    # escamas: coordenadas ao redor da torre (ângulo x altura); barriga lisa do lado da torre
    dr = dr + np.clip(1 - np.abs(dr) / 1.2, 0, 1) * escamas(ang * (RE + 5), Z, r=1.7, prof=0.45) * np.clip((rad - RE - 3) / 2, 0, 1) + pele(g, 0.06, 5)
    # pescoço e cabeça: do fim da espiral até a frente, sobre a entrada
    pf = np.array(pts[-1])
    cab_c = np.array([0, -RE - 6, HT + 16])
    pesc = tubo(g, [tuple(pf), (pf[0] * 0.6, pf[1] - 6, HT + 14), (0, -RE + 2, HT + 16)], [6.5, 6.2, 6.0])
    dr = smin(dr, pesc, 2.5)
    SC, PC = 1.5, (0, -RE + 2, HT + 16)
    gh = Escala(g, PC, SC)
    cab = smin(elipsoide(gh, (0, -RE - 2, HT + 17), (7.5, 9, 6.5)), elipsoide(gh, (0, -RE - 10, HT + 15), (5, 7, 4)), 3)
    queixo = elipsoide(Vista(gh, (0, -RE - 7, HT + 9), rot_x(-25)), (0, -RE - 7, HT + 9.5), (4.2, 7, 2.6))
    cab = smin(cab, queixo, 1.5)
    boca = elipsoide(Vista(gh, (0, -RE - 10, HT + 12), rot_x(-12)), (0, -RE - 10, HT + 12), (3.6, 7, 1.5))
    cab = menos(cab, boca, 0.6) * SC
    dr = smin(dr, cab, 2)
    # patas agarradas na torre
    garras = None
    for (a, z) in [(200, 30), (330, 72), (95, 108)]:
        ar = np.radians(a)
        p0 = np.array([(RE + 4) * np.cos(ar), (RE + 4) * np.sin(ar), z])
        p1 = np.array([(RE + 0.5) * np.cos(ar + 0.18), (RE + 0.5) * np.sin(ar + 0.18), z - 8])
        dr = smin(dr, capsula(g, p0, p1, 3.0, 2.2), 1.5)
        for k in (-1, 0, 1):
            q = p1 + np.array([np.cos(ar + 0.18 + np.pi / 2), np.sin(ar + 0.18 + np.pi / 2), 0]) * k * 2.2
            gr = capsula(g, q, q + np.array([-np.cos(ar) * 1.2, -np.sin(ar) * 1.2, -3.2]), 1.0, 0.35)
            garras = gr if garras is None else np.minimum(garras, gr)
    # espinhos ao longo das costas (para fora)
    esp = None
    for i in range(2, N - 1, 2):
        p = np.array(pts[i]); rdir = np.array([p[0], p[1], 0]) / np.hypot(p[0], p[1])
        s = capsula(g, p + rdir * raios[i] * 0.6, p + rdir * (raios[i] + 3.2) + np.array([0, 0, 1.5]), 1.6, 0.3)
        esp = s if esp is None else np.minimum(esp, s)
    # chifres, dentes, olhos
    claro = esp
    for sx in (-1, 1):
        ch = SC * tubo(gh, [(sx * 4, -RE + 2, HT + 21), (sx * 7, -RE + 7, HT + 26), (sx * 8, -RE + 12, HT + 26)], [2.0, 1.3, 0.4])
        claro = np.minimum(claro, ch)
        for k in range(3):
            d = SC * capsula(gh, (sx * (1.5 + k * 1.3), -RE - 15 + k * 2.5, HT + 13.6), (sx * (1.5 + k * 1.3), -RE - 15 + k * 2.5, HT + 11.6), 0.8, 0.25)
            claro = np.minimum(claro, d)
    claro = np.minimum(claro, garras)
    olhos, pup = None, None
    for sx in (-1, 1):
        o = SC * esfera(gh, (sx * 5.2, -RE - 7, HT + 19.5), 2.2)
        p = SC * elipsoide(gh, (sx * 5.9, -RE - 8.2, HT + 19.6), (0.7, 1.2, 1.6))
        olhos = o if olhos is None else np.minimum(olhos, o)
        pup = p if pup is None else np.minimum(pup, p)
    claro = np.minimum(claro, menos(olhos, pup))
    # asas dobradas nas costas da cabeça (atrás da torre no topo)
    asas = None
    for sx in (-1, 1):
        ga = Escala(g, (sx * 6, 8, HT + 4), 1.6)
        v = Vista(ga, (sx * 14, 6, HT + 10), mul(rot_z(sx * 20), rot_y(sx * -30)))
        mem = np.maximum(np.abs(v.y - 6) - 1.0, np.maximum(np.sqrt((v.x - sx * 14) ** 2 + (v.z - HT - 8) ** 2) - 16,
                                                           -(np.sqrt((v.x - sx * 22) ** 2 + (v.z - HT + 6) ** 2) - 12))) * 1.6
        osso = tubo(v, [(sx * 6, 6, HT + 8), (sx * 16, 6, HT + 24), (sx * 30, 6, HT + 14)], [2.2, 1.6, 0.8]) * 1.6
        for (px, pz) in [(sx * 30, HT + 14), (sx * 24, HT + 2), (sx * 17, HT - 4)]:       # dedos da asa (nervuras)
            osso = np.minimum(osso, tubo(v, [(sx * 16, 6, HT + 24), (px * 0.85 + sx * 2, 6.6, (pz + HT + 24) / 2), (px, 6.8, pz)], [1.2, 0.9, 0.4]) * 1.6)
        mem = mem + 0.1 * ruido(g, 1.0, 6 + sx)
        asas = mem if asas is None else np.minimum(asas, mem)
        dr = smin(dr, np.maximum(osso, -Z + HT - 30), 0.8)
    # barriga (faixa clara do lado de dentro do corpo, encostada na torre)
    barriga = np.maximum(dr + 0.0, rad - RE - 3.2)
    barriga = np.maximum(barriga, -dr - 1.8)
    tudo = np.minimum.reduce([corpo, dr, claro, asas])
    tudo = np.maximum(tudo, -Z)
    escuro = np.maximum(pup, olhos)
    return tudo, {"c3": np.minimum(claro, olhos), "c4": np.minimum(asas, np.maximum(barriga, Z - HT)), "c2": np.minimum(dr, escuro)}


def bandeja(g):
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + (Y - BY) ** 2)
    fora = smin(caixa(g, (0, -30, 9), (74, 62, 9), 10), np.maximum(rad - RE - 7, np.maximum(-Z, Z - 18)), 6)
    fora = np.maximum(fora, np.maximum(-Z, Z - 18))
    dentro = caixa(g, (0, -38, 12), (68, 52, 12), 7)
    corpo = menos(fora, np.maximum(dentro, 3 - Z), 1.5)
    corpo = menos(corpo, np.maximum(rad - RE - 0.3, ZB - Z))          # rebaixo onde a torre assenta
    # borda de pedra (blocos) e calçamento no fundo
    u = np.where(np.abs(X) > 70, Y + 300 * np.sign(X), X)
    perto = np.clip(1 - np.abs(fora) / 1.6, 0, 1)
    corpo = corpo + perto * np.where((Z > 4) & (Z < 17), tijolos(u, Z - 3, larg=16, alt=7, junta=0.6, prof=0.7, semente=7, irregular=0.3), 0)
    lajes = tijolos(X, Y, larg=16, alt=13, junta=0.6, prof=0.6, semente=8, irregular=0.45)
    corpo = corpo + np.where(dentro < -0.8, lajes * np.clip(1 - np.abs(Z - 3) / 0.9, 0, 1), 0) + desgaste(g, 0.3, 9)
    # ossinhos e moedas na bandeja (decoração em relevo baixo no canto)
    tesouro = None
    for (x, y, rz) in [(-52, -76, 20), (-44, -84, -30), (55, -80, 10), (50, -70, 70)]:
        v = Vista(g, (x, y, 3.6), rot_z(rz))
        m = cilindro(v, (x, y, 3), 4.5, 1.8, 0.6)
        m = menos(m, np.maximum(texto2d(v.x - x, v.y - y, "T", 4.0, "serif"), np.abs(v.z - 4.8) - 0.35), 0.1)    # moeda cunhada
        tesouro = m if tesouro is None else np.minimum(tesouro, m)
    tudo = np.minimum(corpo, tesouro)
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": tesouro}


if __name__ == "__main__":
    base_out = saida(__file__, "torre_dragao", False)
    ft = esculpir(torre, (-70, -62, 0), (70, 62, 200), passo, base_out + "-torre")
    fb = esculpir(bandeja, (-80, -102, 0), (80, 72, 22), passo, base_out + "-bandeja")
    for c in ["c1", "c2", "c3", "c4"]:          # foto: torre sobre o rebaixo da bandeja, por cor
        ms = []
        if c in ft:
            m = trimesh.load(ft[c][0])
            m.apply_translation((0, BY, ZB))
            ms.append(m)
        if c in fb:
            ms.append(trimesh.load(fb[c][0]))
        if ms:
            trimesh.util.concatenate(ms).export(f"{base_out}_{c}.stl")
    print("ok", list(ft), list(fb))
