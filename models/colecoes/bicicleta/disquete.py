"""Porta-copos Disquete – 4 porta-copos em forma de disquete de 3½" (94 × 90 × 4 mm) com etiqueta, janela de metal
e trava de proteção em relevo, guardados de pé num estojo de arquivo com divisória e etiqueta "SAVE".
Cores: c1 disquete e estojo, c2 janela de metal e trava, c3 etiqueta, c4 letras.
Impressão (--imprimir): disquetes deitados (etiqueta para cima) e estojo em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.3)
DX, DY, E = 47.0, 45.0, 4.0
NOMES = ["MAPA.DAT", "FICHA.EXE", "SAVE.001", "MESA.BAT"]


def disquete(g, c, nome, rot=None):
    gv = Vista(g, c, rot) if rot is not None else g
    x, y, z = gv.x - c[0], gv.y - c[1], gv.z - c[2]
    d = caixa(gv, c, (DX, DY, E / 2), 2.0)
    d = menos(d, np.maximum(DX + DY - 7 - x - y, np.abs(z) - 3))                                  # canto chanfrado
    topo = np.abs(z - E / 2 - 0.2) - 0.6
    janela = np.maximum(np.maximum(np.abs(x + 6) - 17, np.abs(y + DY - 15) - 15), topo)
    janela = menos(janela, np.maximum(np.maximum(np.abs(x + 2) - 5, np.abs(y + DY - 16) - 10), np.abs(z - E / 2) - 1.5))
    trava = np.maximum(np.maximum(np.abs(x - DX + 8) - 3.4, np.abs(y + DY - 8) - 3.4), topo)
    etiq = np.maximum(np.maximum(np.abs(x) - 36, np.abs(y - 18) - 22), topo)
    sobre = np.abs(z - E / 2 - 0.9) - 0.4
    letras = np.maximum(texto2d(x, y - 26, nome, 6.0, "mono"), sobre)
    linhas = np.maximum(np.maximum(np.abs(np.mod(y - 4, 6) - 3) - 0.35, np.maximum(np.abs(x) - 30, np.abs(y - 10) - 9)), sobre)
    letras = np.minimum(letras, linhas)
    return np.minimum.reduce([d, janela, trava, etiq, letras]), np.minimum(janela, trava), etiq, letras


acc = {"tudo": [], "metal": [], "etiq": [], "letras": []}


def junta(tudo, metal=None, etiq=None, letras=None):
    for k, v in (("tudo", tudo), ("metal", metal), ("etiq", etiq), ("letras", letras)):
        if v is not None:
            acc[k].append(v)


if IMP:
    g = Grade((-50, -48, 0), (50 + 300, 48, 6.5), passo)
    for i, n in enumerate(NOMES):
        junta(*disquete(g, (i * 100, 0, E / 2), n))
else:
    g = Grade((-62, -120, 0), (62, 30, 100), passo)
    est = caixa(g, (0, 0, 30), (52, 22, 30), 3)                                        # estojo aberto em cima
    est = menos(est, caixa(g, (0, 0, 34), (49, 19, 30), 2))
    est = menos(est, np.maximum(np.maximum(np.abs(g.x) - 30, g.y + 10), 40 - g.z), 2)  # frente mais baixa
    save = np.maximum(texto2d(g.x, g.z - 22, "SAVE", 9, "sans"), np.abs(g.y + 22.6) - 0.6)
    junta(est, letras=save)
    for i, n in enumerate(NOMES[1:]):
        junta(*disquete(g, (0, -8 + i * 8, DY + 4.5), n, rot_x(-90)))
    junta(*disquete(g, (0, -76, E / 2), NOMES[0], rot_z(8)))
red = lambda k: acc[k][0] if len(acc[k]) == 1 else np.minimum.reduce(acc[k])
letras = red("letras")
tudo = np.maximum(np.minimum(red("tudo"), letras), -g.z)
partes = dividir(tudo, {"c4": letras, "c3": red("etiq"), "c2": red("metal")})
for k, vv in exportar(g, partes, saida(__file__, "disquete", IMP), faces=None).items():
    print(k, vv)
