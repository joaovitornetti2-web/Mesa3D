"""Chaveiro Fita Cassete – fitinha de 52 × 34 × 6 mm com etiqueta "LADO A", janela com carretéis e furo para
argola no canto. Os dois lados são iguais. Conjunto de 4 na foto.
Cores: c1 fita, c2 janela e carretéis, c3 etiqueta, c4 letras. Deitado, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.12)
LX, LY, E = 26.0, 17.0, 6.0


def chaveiro(g, cx, cy, rz):
    v = Vista(g, (cx, cy, 0), rot_z(rz))
    x, y, z = v.x - cx, v.y - cy, v.z
    c = caixa(v, (cx, cy, E / 2), (LX, LY, E / 2), 2.4)
    c = menos(c, np.maximum(np.sqrt((x + LX - 4.5) ** 2 + (y - LY + 4.5) ** 2) - 2.2, -1))   # furo da argola
    face = lambda zz, s: np.abs(z - zz) - s
    etiq = jan = carr = let = None
    for zz, lado in ((E, 1), (0.0, -1)):
        e = np.maximum(np.maximum(np.abs(x) - 20, np.abs(y - 3) - 11), face(zz, 0.5))
        j = np.maximum(np.maximum(np.abs(x) - 11, np.abs(y - 1) - 4), face(zz, 0.7))
        cr = None
        for xx in (-6.5, 6.5):
            rad = np.sqrt((x - xx) ** 2 + (y - 1) ** 2)
            k = np.maximum(np.maximum(rad - 3.2, 1.6 - rad), face(zz, 0.9))
            cr = k if cr is None else np.minimum(cr, k)
        l_ = np.maximum(texto2d(x * lado, y - 9.5, "LADO A" if lado > 0 else "LADO B", 3.2, "mono"), face(zz, 0.9))
        e = np.minimum(menos(e, j), cr)                      # etiqueta (sem a janela) + carretéis claros
        etiq = e if etiq is None else np.minimum(etiq, e)
        jan = j if jan is None else np.minimum(jan, j)
        carr = cr if carr is None else np.minimum(carr, cr)
        let = l_ if let is None else np.minimum(let, l_)
    escuro = menos(jan, carr)
    return np.minimum.reduce([c, etiq, escuro, let]), escuro, etiq, let


g = Grade((-62, -46, 0), (62, 46, E + 1), passo if IMP else max(passo, 0.15))
tudo = esc = et = le = None
pos = [(-30, 20, 8), (30, 20, -6), (-30, -20, -4), (30, -20, 10)]
for (cx, cy, rz) in pos:
    a, b, c_, d = chaveiro(g, cx, cy, rz)
    tudo = a if tudo is None else np.minimum(tudo, a)
    esc = b if esc is None else np.minimum(esc, b)
    et = c_ if et is None else np.minimum(et, c_)
    le = d if le is None else np.minimum(le, d)
tudo = np.maximum(np.maximum(tudo, -g.z), g.z - E - 0.6)
partes = dividir(tudo, {"c4": le, "c3": et, "c2": esc})
for k, vv in exportar(g, partes, saida(__file__, "chaveiro_fita", IMP), faces=None).items():
    print(k, vv)
