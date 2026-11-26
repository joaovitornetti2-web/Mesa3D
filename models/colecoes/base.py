"""Atalhos comuns das coleções: importa a biblioteca SDF das peças esculpidas e padroniza saída e 3MF."""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(RAIZ), "esculpidos"))
import sdf as _sdf
from sdf import *  # noqa: F401,F403
import numpy as np  # noqa: F401

# ---- float32 em tudo: a Grade original soma um np.float64 às coordenadas e os parâmetros vindos de np.cos etc.
# também são float64, o que dobra a memória de cada campo. Aqui os escalares viram float do Python.


def _f(v):
    if isinstance(v, np.generic):
        return float(v)
    if isinstance(v, (tuple, list)) and v and all(isinstance(t, (int, float, np.generic)) for t in v):
        return tuple(float(t) for t in v)
    if isinstance(v, np.ndarray) and v.ndim == 1 and v.size <= 4:
        return tuple(float(t) for t in v)
    return v


class Grade(_sdf.Grade):
    def __init__(self, mn, mx, passo=0.22):
        super().__init__(_f(tuple(mn)), _f(tuple(mx)), float(passo))
        self.x, self.y, self.z = (a.astype(np.float32) for a in (self.x, self.y, self.z))

    def p(self, c=(0, 0, 0)):
        c = _f(tuple(c))
        return self.x - c[0], self.y - c[1], self.z - c[2]


def _vista_p(self, c=(0, 0, 0)):
    c = _f(tuple(c))
    return self.x - c[0], self.y - c[1], self.z - c[2]


_sdf.Vista.p = _vista_p


def capsula(g, a, b, r1, r2=None):
    a, b, r1 = _f(tuple(a)), _f(tuple(b)), float(r1)
    r2 = r1 if r2 is None else float(r2)
    ba = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    L2 = ba[0] ** 2 + ba[1] ** 2 + ba[2] ** 2
    x, y, z = g.p(a)
    h = np.clip((x * ba[0] + y * ba[1] + z * ba[2]) / L2, 0, 1)
    return np.sqrt((x - ba[0] * h) ** 2 + (y - ba[1] * h) ** 2 + (z - ba[2] * h) ** 2) - (r1 + (r2 - r1) * h)


_sdf.capsula = capsula          # tubo() usa esta


def _embrulha(fn):
    def w(*a, **k):
        return fn(*[_f(x) for x in a], **{kk: _f(v) for kk, v in k.items()})
    w.__name__, w.__doc__ = fn.__name__, fn.__doc__
    return w


for _n in ["esfera", "elipsoide", "toro", "caixa", "cilindro", "smin", "smax", "menos", "casca"]:
    globals()[_n] = _embrulha(getattr(_sdf, _n))
    setattr(_sdf, _n, globals()[_n])


def tubo(g, pontos, raios):
    d = None
    for i in range(len(pontos) - 1):
        s = capsula(g, pontos[i], pontos[i + 1], raios[i], raios[i + 1])
        d = s if d is None else np.minimum(d, s)
    return d


def args(padrao=0.3):
    """passo da grade (1º argumento) e se é a versão de impressão (--imprimir)."""
    nums = [a for a in sys.argv[1:] if not a.startswith("--")]
    return (float(nums[0]) if nums else padrao), ("--imprimir" in sys.argv)


def saida(arquivo, nome, imprimir=False):
    """caminho base dos STL: <coleção>/stl/<nome> (foto) ou <coleção>/stl_imprimir/<nome>."""
    pasta = os.path.join(os.path.dirname(os.path.abspath(arquivo)), "stl_imprimir" if imprimir else "stl")
    return os.path.join(pasta, nome)


def montar_3mf(arquivo, nome, imprimir=True):
    """junta os STL de cada cor num 3MF (um objeto por cor, para escolher o filamento no Bambu Studio)."""
    import trimesh
    base = saida(arquivo, nome, imprimir)
    if not os.path.exists(base + "_c1.stl"):
        base = saida(arquivo, nome, False)
    s = trimesh.Scene()
    for c in ["c1", "c2", "c3", "c4", "c5"]:
        f = f"{base}_{c}.stl"
        if os.path.exists(f):
            m = trimesh.load(f)
            alvo = 450000 if c == "c1" else 150000
            if len(m.faces) > alvo:             # simplifica mantendo o detalhe fino (textura de 0,1–0,2 mm)
                import fast_simplification
                v, fc = fast_simplification.simplify(m.vertices.astype(np.float32), m.faces, 1 - alvo / len(m.faces))
                m = trimesh.Trimesh(v, fc, process=True)
            trimesh.repair.fill_holes(m)          # fecha furinhos de triângulos degenerados
            trimesh.repair.fix_normals(m)
            s.add_geometry(m, node_name=f"{nome}_{c}", geom_name=f"{nome}_{c}")
    out = os.path.join(os.path.dirname(os.path.abspath(arquivo)), f"{nome}.3mf")
    open(out, "wb").write(trimesh.exchange.threemf.export_3MF(s))
    return out


class Escala:
    """a grade vista por um objeto ampliado `s` vezes em torno de `c`; multiplique o campo resultante por s."""
    def __init__(self, g, c, s):
        self.x = ((g.x - c[0]) / s + c[0]).astype(np.float32)
        self.y = ((g.y - c[1]) / s + c[1]).astype(np.float32)
        self.z = ((g.z - c[2]) / s + c[2]).astype(np.float32)
        self.passo, self.shape, self.mn = g.passo / s, g.shape, g.mn

    def p(self, c=(0, 0, 0)):
        return self.x - c[0], self.y - c[1], self.z - c[2]


FONTES = {"serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
          "redonda": os.path.join(os.path.dirname(RAIZ), "decor", "fontes", "Fredoka.ttf"),
          "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
          "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}


def texto2d(u, v, texto, altura, fonte="serif", px_mm=12):
    """campo de distância 2D (mm, < 0 dentro das letras) do texto centrado em (0, 0), letras com `altura` mm."""
    from PIL import Image, ImageDraw, ImageFont
    from scipy import ndimage
    f = ImageFont.truetype(FONTES.get(fonte, fonte), int(altura * px_mm * 1.35))
    x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), texto, font=f)
    pad = int(4 * px_mm)
    im = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - x0, pad - y0), texto, font=f, fill=255)
    a = np.array(im) > 127
    sd = (ndimage.distance_transform_edt(~a) - ndimage.distance_transform_edt(a)) / px_mm
    esc = altura / ((y1 - y0) / px_mm) if texto.strip() else 1.0
    h, w = a.shape
    # (u, v) em mm -> pixel (linha, coluna); v para cima
    col = (np.asarray(u) / esc) * px_mm + w / 2
    lin = -(np.asarray(v) / esc) * px_mm + h / 2
    U, V = np.broadcast_arrays(col, lin)
    out = ndimage.map_coordinates(sd, [V.ravel(), U.ravel()], order=1, mode="constant", cval=sd.max())
    return (out.reshape(U.shape) * esc).astype(np.float32)
