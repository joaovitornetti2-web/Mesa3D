"""Contador de Vida – marcador de pontos de vida de 0 a 99: duas rodas numeradas (dezenas e unidades) giram
num eixo dentro de um suporte de pedra com frente de escudo; a janela do escudo mostra o número e as rodas saem por
cima para girar com o polegar. Coração em relevo no topo do escudo.
Peças: suporte, 2 rodas e o pino do eixo (Ø 3 mm, entra pela lateral). 66 × 34 × 52 mm.
Cores: c1 suporte, c2 rodas, c3 números, c4 coração. Rodas deitadas, suporte em pé, sem suporte.
Ainda não testado: folga das rodas no pino (0,25 mm) e o encaixe justo do pino nas laterais."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
RW, ZC, LW = 15.0, 22.0, 10.0          # raio da roda, altura do eixo, largura da roda
MOSTRA = (2, 0)                        # número na foto: 20
MN, MX = (-36, -25, 0), (36 + (66 if IMP else 0), 20, 54)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 1.0, 6)


    def roda(xc, mostra, gg=None):
        X, Y, Z = (gg.x, gg.y, gg.z) if gg is not None else (g.x, g.y, g.z)
        rad = np.sqrt(Y ** 2 + (Z - ZC) ** 2)
        corpo = np.maximum(rad - RW, np.abs(X - xc) - LW / 2)
        corpo = smax(corpo, np.abs(X - xc) - LW / 2, 0.8)
        corpo = menos(corpo, rad - 1.75)                                         # furo do eixo
        # ranhuras para o dedo nas laterais da borda (serrilhado)
        th = np.arctan2(Z - ZC, -Y)
        serr = np.abs(np.mod(th * 40 / (2 * np.pi), 1) - 0.5) * 2 - 0.5
        corpo = menos(corpo, np.maximum(np.maximum(-(rad - RW + 0.8), np.abs(np.abs(X - xc) - LW / 2) - 0.8), serr), 0.2)
        nums = None
        for d in range(10):
            phi = np.radians((d - mostra) * 36)
            dth = np.angle(np.exp(1j * (th - phi)))
            t = texto2d((X - xc), dth * RW, str(d), 7.5, "serif")
            t = np.maximum(t, np.abs(dth) - np.radians(17))
            nums = t if nums is None else np.minimum(nums, t)
        nums = np.maximum(nums, np.abs(rad - RW - 0.3) - 0.6)
        return np.minimum(corpo, nums), nums


    if IMP:
        # rodas deitadas ao lado (eixo vertical) e o pino do eixo
        def deitada(cx):
            v = Vista(g, (cx, 0, LW / 2), rot_y(90))
            v.x, v.z = v.x - cx, v.z - LW / 2 + ZC
            return v
        r1, n1 = roda(0.0, 0, deitada(52))
        r2, n2 = roda(0.0, 0, deitada(84))
        pino = np.maximum(capsula(g, (40, 17, 1.5), (68, 17, 1.5), 1.5), -g.z)
    else:
        r1, n1 = roda(-6.0, MOSTRA[0])
        r2, n2 = roda(6.0, MOSTRA[1])
        pino = None
    # suporte: base, laterais com furo do eixo, frente de escudo com janela
    base = caixa(g, (0, 2, 2), (31, 15, 2), 1.5) + rr * 0.15
    lat = None
    for sx in (-1, 1):
        l = caixa(g, (sx * 13.5, 2, ZC - 1), (2.2, 13, ZC - 1), 1.2) + rr * 0.06
        lat = l if lat is None else np.minimum(lat, l)
    lat = menos(lat, np.maximum(np.sqrt(Y ** 2 + (Z - ZC) ** 2) - 1.6, np.abs(X) - 20))   # furo do pino (justo)
    W, H1, R = 31.0, 46.0, 45.0
    e2 = np.minimum(np.maximum(np.abs(X) - W, Z - 30), (np.sqrt((X / W) ** 2 + ((Z - 30) / 16) ** 2) - 1) * 14)   # placa com topo em arco
    e2 = np.maximum(e2, -Z)
    esc = np.maximum(e2, np.abs(Y + RW + 3) - 2.0) + rr * 0.06
    mold = np.maximum(np.maximum(e2, -(e2 + 2.6)), np.abs(Y + RW + 5.6) - 0.7)                  # moldura saltada na frente
    esc = smin(esc, mold, 0.4)
    esc = smin(esc, np.maximum(np.maximum(e2 + 4.2, -(e2 + 5.0)), np.abs(Y + RW + 5.2) - 0.35), 0.2)   # filete interno
    jan = np.maximum(np.abs(X) - 11.5, np.abs(Z - ZC) - 5.5)
    esc = menos(esc, np.maximum(jan, np.abs(Y + RW + 3) - 4), 0.8)
    # pedra na base, rebites na moldura, folhas de louro em volta do coração
    base = base + desgaste(g, 0.3, 7) + np.clip(1 - np.abs(base) / 1.2, 0, 1) * tijolos(X, Y, larg=10, alt=8, junta=0.4, prof=0.0, irregular=0.3, semente=8) * 0.5
    esc = np.minimum(esc, rebites(g, [(sx * 29.7, -RW - 6.3, zz) for sx in (-1, 1) for zz in (4, 12, 20, 28)] + [(29.7 * np.cos(a), -RW - 6.3, 30 + 14.7 * np.sin(a)) for a in np.linspace(0.35, np.pi - 0.35, 5)], 0.9))
    esc = esc + 0.05 * ruido(g, 1.2, 9)
    for sx in (-1, 1):
        for k in range(5):
            a = np.radians(200 - k * 22) if sx < 0 else np.radians(-20 + k * 22)
            px, pz = 9.5 * np.cos(a), 37 + 7 * np.sin(a) - 2
            folha = elipsoide(Vista(g, (px, -RW - 5.4, pz), rot_y(np.degrees(a) + 90)), (px, -RW - 5.4, pz), (1.4, 0.9, 2.8))
            esc = smin(esc, folha, 0.3)
    suporte = np.minimum.reduce([base, lat, esc])
    # coração no topo do escudo
    hx, hz = X, Z - 37.0
    coracao = np.minimum(np.sqrt((hx - 2.6) ** 2 + (hz - 1.2) ** 2) - 3.0, np.sqrt((hx + 2.6) ** 2 + (hz - 1.2) ** 2) - 3.0)
    coracao = np.minimum(coracao, np.maximum(1.05 * np.abs(hx) - (hz + 5.8), hz - 1.5))
    coracao = np.maximum(coracao, np.abs(Y + RW + 5.6) - 1.0)
    tudo = np.minimum.reduce([suporte, r1, r2, coracao] + ([pino] if pino is not None else []))
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c3": np.minimum(n1, n2), "c2": np.minimum(r1, r2), "c4": coracao}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "contador", IMP)).items():
        print(k, v)
