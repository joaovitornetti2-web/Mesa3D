"""Olho Vigia – luminária: um globo ocular de parede fina (1,4 mm, brilha em PLA branco com uma vela de LED
dentro) seguro por quatro garras que saem de um toco retorcido. A íris e as veias são relevo; a pupila é vazada,
então a luz escapa pelo centro do olhar. Base oca com entrada por baixo para a vela de LED (Ø 40 mm).
Ø 74 × 104 mm. Cores: c1 base e garras, c2 pupila, c3 globo, c4 íris e veias.
Em pé, sem suporte (globo autoportante; a abertura de baixo tem chanfro de 45°)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.3)
RO, CZ, E = 30.0, 64.0, 1.4
MN, MX = (-40, -40, 0), (40, 40, 100)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    rr = ruido(g, 1.8, 81)
    rad = np.sqrt(X ** 2 + Y ** 2)
    # base: toco retorcido oco
    tw = np.arctan2(Y, X) + Z * 0.05
    toco = np.maximum(rad - (27 - Z * 0.12) - 1.5 * np.sin(tw * 5), np.maximum(-Z, Z - 41)) + rr * 0.4
    toco = smin(toco, np.maximum(rad - 33 - 2 * np.sin(np.arctan2(Y, X) * 6), np.maximum(-Z, Z - 5)) + rr * 0.5, 4)
    tunel = np.minimum(np.maximum(rad - 20.5, np.maximum(-1 - Z, Z - 20)), np.maximum(rad - (20.5 - (Z - 20) * 0.45), np.maximum(20 - Z, Z - 50)))
    toco = menos(toco, tunel)                                             # túnel da vela de LED, afunila até o globo
    toco = menos(toco, np.maximum(np.sqrt(X ** 2 + Y ** 2 + (Z - CZ) ** 2) - RO + 0.5, 30 - Z))   # não invade o globo
    # globo: casca fina com abertura embaixo
    d = np.sqrt(X ** 2 + Y ** 2 + (Z - CZ) ** 2)
    globo = np.maximum(np.abs(d - RO + E / 2) - E / 2, -(Z - CZ + RO - 4))
    # garras segurando o globo
    garras = None
    for k in range(4):
        a = np.radians(45 + k * 90)
        ca, sa = np.cos(a), np.sin(a)
        p = [(16 * ca, 16 * sa, 30), (27 * ca, 27 * sa, 46), (31 * ca, 31 * sa, 62), (25 * ca, 25 * sa, 80), (17 * ca, 17 * sa, 87)]
        gr = tubo(g, p, [4.2, 3.4, 2.8, 2.0, 1.0])
        garras = gr if garras is None else np.minimum(garras, gr)
    toco = smin(toco, garras, 2.5)
    # íris e pupila voltadas para a frente (−y), olhando um pouco para cima
    dirv = np.array([0.0, -0.94, 0.34])
    cosang = (X * dirv[0] + Y * dirv[1] + (Z - CZ) * dirv[2]) / np.maximum(d, 1e-6)
    ang = np.arccos(np.clip(cosang, -1, 1))
    iris = np.maximum(ang * RO - 13, np.abs(d - RO - 0.2) - 0.6)
    pupila = np.maximum(ang * RO - 5.5, np.abs(d - RO + E / 2) - E)
    globo = menos(globo, pupila)                                            # pupila vazada
    iris = menos(iris, pupila)
    anel = np.maximum(np.abs(ang * RO - 9.5) - 0.5, np.abs(d - RO - 0.5) - 0.4)
    # veias saindo de trás para a íris
    veias = None
    for k in range(7):
        b = np.radians(k * 51 + 10)
        pts = []
        for t in np.linspace(0, 1, 5):
            th = np.radians(150 - 105 * t)                                  # do fundo até perto da íris
            q = np.array([np.sin(th) * np.cos(b + 0.4 * np.sin(t * 6 + k)), np.sin(th) * np.sin(b + 0.4 * np.sin(t * 6 + k)), np.cos(th)])
            # gira a base local (eixo = dirv)
            z_ = dirv; x_ = np.cross([0, 0, 1.0], z_); x_ /= np.linalg.norm(x_); y_ = np.cross(z_, x_)
            w = q[0] * x_ + q[1] * y_ + q[2] * z_
            pts.append(tuple(np.array([0, 0, CZ]) + w * (RO + 0.5)))
        v = tubo(g, pts, [0.7, 0.9, 1.0, 0.9, 0.6])
        veias = v if veias is None else np.minimum(veias, v)
    veias = np.maximum(veias, -(d - RO + 0.3))
    cor4 = np.minimum.reduce([iris, anel, veias])
    tudo = np.minimum.reduce([toco, globo, cor4])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c4": cor4, "c3": globo}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "olho", IMP)).items():
        print(k, v)
