"""Mini-biblioteca de escultura por campos de distância (SDF) para as peças do Ateliê do Mestre.

Em vez de juntar sólidos duros (cara de OpenSCAD/iniciante), cada peça é um campo contínuo:
as formas se fundem com uniões suaves (como argila), recebem dobras, rugas e textura de mão,
e cada cor do AMS é uma região do mesmo campo (as peças de cor encaixam sem folga nem fresta).

Uso típico:
    g = Grade((-30, -30, 0), (30, 30, 60), passo=0.22)
    corpo = smin(esfera(g, (0,0,30), 15), capsula(g, ...), 4)
    exportar(g, {"c1": corpo_c1, "c2": olhos}, "saida/boo")
"""
import os

import numpy as np
from scipy import ndimage

PHI = (1 + 5 ** 0.5) / 2


class Grade:
    def __init__(self, mn, mx, passo=0.22):
        self.passo = passo
        self.mn = np.array(mn, float)
        n = np.ceil((np.array(mx, float) - self.mn) / passo).astype(int) + 1
        self.shape = tuple(n)
        ax = [self.mn[i] + np.arange(n[i], dtype=np.float32) * passo for i in range(3)]
        self.x, self.y, self.z = np.meshgrid(*ax, indexing="ij", sparse=True)

    def p(self, c=(0, 0, 0)):
        return self.x - c[0], self.y - c[1], self.z - c[2]


# ---------------- primitivas ----------------
def esfera(g, c, r):
    x, y, z = g.p(c)
    return np.sqrt(x * x + y * y + z * z) - r


def elipsoide(g, c, r):
    """aproximação boa de elipsoide (iq)."""
    x, y, z = g.p(c)
    rx, ry, rz = r
    k0 = np.sqrt((x / rx) ** 2 + (y / ry) ** 2 + (z / rz) ** 2)
    k1 = np.sqrt((x / rx ** 2) ** 2 + (y / ry ** 2) ** 2 + (z / rz ** 2) ** 2)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-6)


def capsula(g, a, b, r1, r2=None):
    """tubo de a até b com raio indo de r1 a r2 (cone arredondado)."""
    r2 = r1 if r2 is None else r2
    a, b = np.array(a, float), np.array(b, float)
    ba = b - a
    x, y, z = g.p(a)
    h = np.clip((x * ba[0] + y * ba[1] + z * ba[2]) / ba.dot(ba), 0, 1)
    return np.sqrt((x - ba[0] * h) ** 2 + (y - ba[1] * h) ** 2 + (z - ba[2] * h) ** 2) - (r1 + (r2 - r1) * h)


def tubo(g, pontos, raios):
    """vários segmentos de capsula seguindo uma curva (cauda, chifre curvo, chapéu torto)."""
    d = None
    for i in range(len(pontos) - 1):
        s = capsula(g, pontos[i], pontos[i + 1], raios[i], raios[i + 1])
        d = s if d is None else np.minimum(d, s)
    return d


def toro(g, c, R, r, achata=1.0):
    x, y, z = g.p(c)
    q = np.sqrt(x * x + y * y) - R
    return np.sqrt(q * q + (z / achata) ** 2) - r


def caixa(g, c, meio, raio=0.0):
    x, y, z = g.p(c)
    qx, qy, qz = np.abs(x) - meio[0] + raio, np.abs(y) - meio[1] + raio, np.abs(z) - meio[2] + raio
    fora = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
    return fora + np.minimum(np.maximum(qx, np.maximum(qy, qz)), 0) - raio


def cilindro(g, c, r, h, raio=0.0):
    x, y, z = g.p(c)
    dx = np.sqrt(x * x + y * y) - r + raio
    dz = np.abs(z - h / 2) - h / 2 + raio
    return np.minimum(np.maximum(dx, dz), 0) + np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dz, 0) ** 2) - raio


def d20(g, c, r, raio=0.5, rot=None):
    """icosaedro (dado d20) com arestas arredondadas. r = raio da esfera inscrita."""
    ns = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for s3 in (-1, 1):
                ns.append((s1, s2, s3))
            ns += [(0, s1 / PHI, s2 * PHI), (s1 / PHI, s2 * PHI, 0), (s1 * PHI, 0, s2 / PHI)]
    ns = np.unique(np.round(np.array(ns, float), 6), axis=0)
    ns /= np.linalg.norm(ns, axis=1)[:, None]
    if rot is not None:
        ns = ns @ np.array(rot).T
    x, y, z = g.p(c)
    d = None
    for n in ns:
        t = x * n[0] + y * n[1] + z * n[2]
        d = t if d is None else np.maximum(d, t)
    return d - (r - raio) - raio * 0.6


# ---------------- operações ----------------
def smin(a, b, k):
    """união suave: as formas se fundem como argila (k = tamanho da 'massa' na junta, mm)."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def menos(a, b, k=0.0):
    """corta b de a (com borda suave se k > 0)."""
    return smax(a, -b, k) if k > 0 else np.maximum(a, -b)


def casca(d, e):
    return np.abs(d) - e / 2


def ruido(g, escala=2.0, semente=1):
    """ruído suave (textura de argila/tecido) com média 0 e desvio ~1."""
    rng = np.random.default_rng(semente)
    r = rng.standard_normal(g.shape).astype(np.float32)
    r = ndimage.gaussian_filter(r, escala / g.passo, mode="wrap")
    return r / (r.std() + 1e-9)


def rot_z(ang):
    a = np.radians(ang)
    return [[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]


def rot_x(ang):
    a = np.radians(ang)
    return [[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]]


# ---------------- divisão em cores e exportação ----------------
def dividir(total, regioes, prioridade=None):
    """Separa o sólido `total` em cores. regioes = {"c2": campo, ...}: onde o campo < 0 é aquela cor
    (só dentro do sólido); o resto é c1. As faces entre cores são compartilhadas (encaixe perfeito)."""
    out = {}
    resto = total
    tomado = None
    for nome, campo in regioes.items():
        c = campo if tomado is None else np.maximum(campo, -tomado)
        out[nome] = np.maximum(total, c)
        resto = np.maximum(resto, -campo)
        tomado = campo if tomado is None else np.minimum(tomado, campo)
    out["c1"] = resto
    return out


def malha(g, campo, suaviza=6, faces=None):
    import trimesh
    from skimage import measure

    if campo.min() >= 0:
        return None
    pad = np.pad(campo, 1, constant_values=1.0)
    v, f, _, _ = measure.marching_cubes(pad, 0.0, spacing=(g.passo,) * 3)
    v = v - g.passo + g.mn
    m = trimesh.Trimesh(v, f[:, ::-1], process=True)
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    if faces and len(m.faces) > faces:
        try:
            import fast_simplification

            vv, ff = fast_simplification.simplify(m.vertices.astype(np.float32), m.faces, 1 - faces / len(m.faces))
            m = trimesh.Trimesh(vv, ff, process=True)
        except Exception:
            pass
    if suaviza:
        trimesh.smoothing.filter_taubin(m, iterations=suaviza)
    return m


def exportar(g, partes, base, faces=250000, ordem=None):
    """partes = {"c1": campo, "c2": campo, ...} -> base_c1.stl, base_c2.stl ... (mm, z = 0 na mesa)."""
    os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
    feitos = {}
    for nome, campo in partes.items():
        m = malha(g, campo, faces=faces if nome == "c1" else faces // 3)
        if m is None:
            continue
        caminho = f"{base}_{nome}.stl"
        m.export(caminho)
        feitos[nome] = (caminho, len(m.faces), round(float(m.volume) / 1000, 2) if m.is_volume else None)
    return feitos


class Vista:
    """a mesma grade vista por um objeto girado em torno de `c` (rot = matriz 3x3 do objeto)."""
    def __init__(self, g, c, rot):
        R = np.array(rot, float).T   # inverso
        x, y, z = g.x - c[0], g.y - c[1], g.z - c[2]
        self.x = (R[0, 0] * x + R[0, 1] * y + R[0, 2] * z).astype(np.float32) + c[0]
        self.y = (R[1, 0] * x + R[1, 1] * y + R[1, 2] * z).astype(np.float32) + c[1]
        self.z = (R[2, 0] * x + R[2, 1] * y + R[2, 2] * z).astype(np.float32) + c[2]
        self.passo, self.shape, self.mn = g.passo, g.shape, g.mn

    def p(self, c=(0, 0, 0)):
        return self.x - c[0], self.y - c[1], self.z - c[2]


def rot_y(ang):
    a = np.radians(ang)
    return [[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]]


def mul(*ms):
    r = np.eye(3)
    for m in ms:
        r = r @ np.array(m)
    return r
