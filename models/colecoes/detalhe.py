"""Kit de detalhe das coleções (versão 2): escultura em fatias, ruído por coordenada e texturas.

Cada peça define `campo(g) -> (tudo, regioes)` (regioes = dict ordenado {"c2": campo, ...}, como em dividir) e chama
    esculpir(campo, mn, mx, passo, base)
A grade é avaliada em fatias ao longo de x (com processos em paralelo), cada fatia vira malha por marching cubes e as
fatias são costuradas pelos vértices do plano comum. Assim dá para usar passo de 0,1 a 0,15 mm em peças grandes.

O ruído aqui depende só da posição (x, y, z) – é igual em qualquer fatia ou resolução –, ao contrário do ruído da
biblioteca antiga, que era sorteado por índice de voxel.
"""
import multiprocessing as mp
import os

import numpy as np

from base import *  # noqa: F401,F403
import base as _base


# ---------------------------------------------------------------- ruído por coordenada
def _hash(i, j, k, s):
    h = (i.astype(np.int64) * 73856093) ^ (j.astype(np.int64) * 19349663) ^ (k.astype(np.int64) * 83492791) ^ (s * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return ((h & 0xFFFF).astype(np.float32) / 32767.5) - 1.0


def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def ruido_xyz(x, y, z, escala=2.0, semente=1):
    """value noise suave em mm (célula = `escala` mm), média 0, desvio ~1."""
    x, y, z = np.broadcast_arrays(np.asarray(x, np.float32) / escala, np.asarray(y, np.float32) / escala,
                                  np.asarray(z, np.float32) / escala)
    xi, yi, zi = np.floor(x), np.floor(y), np.floor(z)
    fx, fy, fz = _fade(x - xi), _fade(y - yi), _fade(z - zi)
    xi, yi, zi = xi.astype(np.int64), yi.astype(np.int64), zi.astype(np.int64)
    out = np.zeros(x.shape, np.float32)
    for dx in (0, 1):
        wx = fx if dx else 1 - fx
        for dy in (0, 1):
            wy = fy if dy else 1 - fy
            for dz in (0, 1):
                wz = fz if dz else 1 - fz
                out += wx * wy * wz * _hash(xi + dx, yi + dy, zi + dz, semente)
    return out * 2.6


def _pesos(eixo, escala):
    """matriz de interpolação (n pontos x células) com fade quíntico, e o índice da 1ª célula."""
    t = np.asarray(eixo, np.float64).ravel() / escala
    i0 = int(np.floor(t.min()))
    i = np.floor(t).astype(np.int64)
    f = _fade(t - i)
    n = int(i.max()) - i0 + 2
    W = np.zeros((t.size, n), np.float32)
    r = np.arange(t.size)
    W[r, i - i0] = 1 - f
    W[r, i - i0 + 1] = f
    return W, i0, n


def _eixos(g):
    """se a grade é alinhada aos eixos (meshgrid esparso), devolve os 3 vetores de coordenadas."""
    x, y, z = g.x, g.y, g.z
    if x.ndim == 3 and x.shape[1] == x.shape[2] == 1 and y.shape[0] == y.shape[2] == 1 and z.shape[0] == z.shape[1] == 1:
        return x.ravel(), y.ravel(), z.ravel()
    return None


def ruido(g, escala=2.0, semente=1):
    """substitui o ruído antigo (gaussiano com sigma = escala): mesma assinatura e mesmo 'tamanho de grão'."""
    return ruido_cel(g, escala * 2.5, semente)


def ruido_cel(g, escala=2.0, semente=1):
    """ruído por coordenada com célula de `escala` mm (seguro em fatias). Grade alinhada aos eixos: interpolação
    separável (rápida); vistas giradas: caminho geral."""
    e = _eixos(g)
    if e is None:
        return ruido_xyz(g.x, g.y, g.z, escala, semente)
    (Wx, ix, nx), (Wy, iy, ny), (Wz, iz, nz) = (_pesos(a, escala) for a in e)
    I, J, K = np.meshgrid(np.arange(ix, ix + nx), np.arange(iy, iy + ny), np.arange(iz, iz + nz), indexing="ij")
    Lt = _hash(I, J, K, semente)
    t = np.tensordot(Wx, Lt, (1, 0))                    # (Nx, ny, nz)
    t = np.tensordot(t, Wy, (1, 1))                     # (Nx, nz, Ny)
    t = np.tensordot(t, Wz, (1, 1))                     # (Nx, Ny, Nz)
    return (t * 2.6).astype(np.float32)


def fbm(g, escala=2.0, semente=1, oitavas=3):
    """ruído com várias escalas (pedra, casca, pele)."""
    r, a, t = 0, 1.0, 0
    for o in range(oitavas):
        r = r + a * ruido_cel(g, escala / 2 ** o, semente + 17 * o)
        t += a
        a *= 0.5
    return r / t


_base.ruido = ruido
_base._sdf.ruido = ruido


def acaso2(i, j, s=1):
    """número em [-1, 1] por célula inteira (i, j)."""
    i, j = np.broadcast_arrays(np.asarray(i), np.asarray(j))
    return _hash(i, j, np.zeros_like(i, dtype=np.int64), s)


# ---------------------------------------------------------------- texturas (devolvem deslocamento em mm; somar ao campo)
def tijolos(u, v, larg=8.0, alt=4.5, junta=0.55, prof=0.6, semente=3, irregular=0.25):
    """alvenaria de pedra: sulcos de argamassa (fileiras desencontradas), blocos com alturas e chanfros diferentes.
    u = direção horizontal ao longo da parede (mm), v = vertical. Soma > 0 remove material."""
    fila = np.floor(v / alt)
    uu = u / larg + 0.5 * (fila % 2) + 0.18 * acaso2(fila, 0, semente)
    col = np.floor(uu)
    fu = (uu - col) * larg
    fv = (v / alt - fila) * alt
    d = np.minimum(np.minimum(fu, larg - fu), np.minimum(fv, alt - fv))        # distância até a junta
    sulco = prof * np.clip(1 - d / junta, 0, 1) ** 1.5
    bloco = irregular * 0.5 * (acaso2(col, fila, semente + 1) + 1)              # blocos mais altos/baixos
    chanfro = 0.25 * prof * np.clip(1 - d / (junta * 3), 0, 1)
    return sulco + chanfro + bloco * prof


def madeira(u, v, tabua=9.0, fenda=0.45, prof=0.5, veio=0.12, semente=5):
    """tábuas ao longo de u (largura `tabua` em v) com fendas entre elas e veios finos."""
    t = np.floor(v / tabua)
    fv = v - t * tabua
    d = np.minimum(fv, tabua - fv)
    fenda_ = prof * np.clip(1 - d / fenda, 0, 1) ** 1.2
    fase = 7 * acaso2(t, 1, semente)
    veios = veio * np.sin(v * 3.1 + 1.6 * np.sin(u * 0.21 + fase) + 0.8 * np.sin(u * 0.067 + 2 * fase))
    nos = 0.18 * np.clip(1 - np.hypot((np.mod(u + 13 * fase, 37) - 18.5) / 3.0, (fv - tabua / 2) / 1.6), 0, 1)
    return fenda_ + veios + nos


def escamas(u, v, r=1.6, prof=0.35):
    """escamas sobrepostas (fileiras desencontradas), como de dragão ou réptil."""
    fila = np.floor(v / (r * 1.1))
    uu = u / (r * 1.8) + 0.5 * (fila % 2)
    cu = (np.floor(uu) + 0.5 - 0.5 * (fila % 2)) * r * 1.8
    cv = (fila + 1.0) * r * 1.1
    dd = np.hypot(u - cu, (v - cv) * 0.9) / (r * 1.15)
    return prof * np.clip(dd, 0, 1) ** 2


def pele(g, prof=0.12, semente=9):
    """pele/argila: textura fina de mão para orgânicos."""
    return prof * fbm(g, 1.2, semente, 2)


def desgaste(g, prof=0.25, semente=11):
    """lascas e amassados em pedra e metal velho (só remove)."""
    return prof * np.clip(fbm(g, 3.0, semente, 2) - 0.3, 0, None) * 2


def rebites(g, pontos, r=0.9):
    d = None
    for p in pontos:
        e = esfera(g, p, r)
        d = e if d is None else np.minimum(d, e)
    return d


def anel(g, c, R, r, eixo="z"):
    """toro em qualquer eixo."""
    x, y, z = g.p(c)
    if eixo == "x":
        x, z = z, x
    elif eixo == "y":
        y, z = z, y
    return np.sqrt((np.sqrt(x ** 2 + y ** 2) - R) ** 2 + z ** 2) - r


def chanfro_caixa(g, c, meio, raio, chanfro):
    """caixa com aresta chanfrada (bisel plano), mais 'de oficina' que arredondada."""
    x, y, z = g.p(c)
    q = [np.abs(x) - meio[0], np.abs(y) - meio[1], np.abs(z) - meio[2]]
    b = caixa(g, c, meio, raio)
    s = (q[0] + q[1] + q[2] + chanfro) / np.sqrt(3)
    return np.maximum(b, s)


def poligono2d(u, v, pts):
    """distância assinada 2D a um polígono (lista de (u, v))."""
    pts = [(float(a), float(b)) for a, b in pts]
    d = None
    s = np.ones(np.broadcast(u, v).shape, np.float32)
    n = len(pts)
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[i - 1]
        ex, ey = bx - ax, by - ay
        wx, wy = u - ax, v - ay
        h = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
        dd = (wx - ex * h) ** 2 + (wy - ey * h) ** 2
        d = dd if d is None else np.minimum(d, dd)
        c1 = v >= ay
        c2 = v < by
        c3 = ex * wy > ey * wx
        m = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(m, -s, s)
    return s * np.sqrt(d)


def extrusao(d2, z, z0, z1):
    """extruda um campo 2D entre z0 e z1."""
    return np.maximum(d2, np.maximum(z0 - z, z - z1))


def sigilo_sangue(u, v, alto=10.0, esp=0.9):
    """Marca de Sangue (Ordem Paranormal): linha vertical com duas bifurcações para os lados, como uma cruz invertida."""
    def seg(ax, ay, bx, by):
        ex, ey = bx - ax, by - ay
        h = np.clip(((u - ax) * ex + (v - ay) * ey) / (ex * ex + ey * ey), 0, 1)
        return np.hypot(u - ax - ex * h, v - ay - ey * h)
    a = alto / 2
    d = seg(0, -a, 0, a)
    d = np.minimum(d, seg(0, -a * 0.35, -a * 0.55, -a * 0.75))
    d = np.minimum(d, seg(0, -a * 0.35, a * 0.55, -a * 0.75))
    return d - esp / 2


# ---------------------------------------------------------------- escultura em fatias
class _GradeN:
    """grade com tamanho exato (para as fatias encostarem sem erro de arredondamento)."""
    def __init__(self, mn, n, passo):
        self.passo = float(passo)
        self.mn = np.array(mn, float)
        self.shape = tuple(int(k) for k in n)
        ax = [np.float32(self.mn[i]) + np.arange(self.shape[i], dtype=np.float32) * np.float32(passo) for i in range(3)]
        self.x, self.y, self.z = np.meshgrid(*ax, indexing="ij", sparse=True)

    def p(self, c=(0, 0, 0)):
        c = _base._f(tuple(c))
        return self.x - c[0], self.y - c[1], self.z - c[2]


_JOB = {}


def _fatia(args):
    i0, i1 = args
    from skimage import measure
    campo, mn, n, passo, nx = _JOB["campo"], _JOB["mn"], _JOB["n"], _JOB["passo"], _JOB["nx"]
    g = _GradeN((mn[0] + i0 * passo, mn[1], mn[2]), (i1 - i0 + 1, n[1], n[2]), passo)
    tudo, regioes = campo(g)
    tudo = np.asarray(tudo, np.float32)
    bordas = {"y-": tudo[:, 0, :], "y+": tudo[:, -1, :], "z+": tudo[:, :, -1]}
    if i0 == 0:
        bordas["x-"] = tudo[0]
    if i1 == nx - 1:
        bordas["x+"] = tudo[-1]
    lados = [k for k, b in bordas.items() if float(b.min()) < 0]
    if lados:
        print(f"AVISO: a peça encosta na borda da grade em {lados}; aumente MN/MX", flush=True)
    partes = dividir(tudo, regioes)
    out = {}
    for cor, c in partes.items():
        c = np.asarray(c, np.float32)
        if c.min() >= 0:
            continue
        px0 = 1 if i0 == 0 else 0
        px1 = 1 if i1 == nx - 1 else 0
        pad = np.pad(c, ((px0, px1), (1, 1), (1, 1)), constant_values=1.0)
        try:
            v, f, _, _ = measure.marching_cubes(pad, 0.0, spacing=(passo,) * 3)
        except (ValueError, RuntimeError):
            continue
        v[:, 0] += mn[0] + (i0 - px0) * passo
        v[:, 1] += mn[1] - passo
        v[:, 2] += mn[2] - passo
        out[cor] = (np.round(v, 4).astype(np.float32), f[:, ::-1].astype(np.int64))
    return out


def esculpir(campo, mn, mx, passo, base, suaviza=3, vox=18e6, procs=None, min_area=3.0):
    """avalia campo(g) em fatias e grava base_<cor>.stl. Devolve {cor: (arquivo, faces)}."""
    import trimesh
    mn = np.array(mn, float)
    n = np.ceil((np.array(mx, float) - mn) / passo).astype(int) + 1
    nx = int(n[0])
    larg = max(6, int(vox / (n[1] * n[2])))
    cortes = list(range(0, nx - 1, larg)) + [nx - 1]
    tarefas = [(cortes[i], cortes[i + 1]) for i in range(len(cortes) - 1)]
    _JOB.update(campo=campo, mn=mn, n=n, passo=float(passo), nx=nx)
    procs = procs or int(os.environ.get("PROCS", 3))
    if procs > 1 and len(tarefas) > 1:
        from concurrent.futures import ProcessPoolExecutor
        from concurrent.futures.process import BrokenProcessPool
        try:
            with ProcessPoolExecutor(min(procs, len(tarefas)), mp_context=mp.get_context("fork")) as ex:
                res = list(ex.map(_fatia, tarefas))
        except BrokenProcessPool:          # um processo morreu (memória): refaz em série em vez de travar
            print("AVISO: processo de fatia morreu; refazendo em série", flush=True)
            res = [_fatia(t) for t in tarefas]
    else:
        res = [_fatia(t) for t in tarefas]
    os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
    feitos = {}
    cores = sorted({c for r in res for c in r})
    for cor in cores:
        vs, fs, off = [], [], 0
        for r in res:
            if cor in r:
                v, f = r[cor]
                vs.append(v)
                fs.append(f + off)
                off += len(v)
        m = trimesh.Trimesh(np.concatenate(vs), np.concatenate(fs), process=True)
        m.merge_vertices(digits_vertex=4)
        m.update_faces(m.nondegenerate_faces())
        m.remove_unreferenced_vertices()
        partes = m.split(only_watertight=False)
        if len(partes) > 1:
            boas = [p for p in partes if p.area >= min_area]
            m = trimesh.util.concatenate(boas) if boas else m
        if suaviza:
            trimesh.smoothing.filter_taubin(m, iterations=suaviza)
        caminho = f"{base}_{cor}.stl"
        m.export(caminho)
        feitos[cor] = (caminho, len(m.faces))
    for f in os.listdir(os.path.dirname(base) or "."):           # apaga cores que sumiram desta versão
        nome = os.path.join(os.path.dirname(base), f)
        if f.startswith(os.path.basename(base) + "_c") and f.endswith(".stl") and f[len(os.path.basename(base)) + 1:-4] not in cores:
            os.remove(nome)
    return feitos


def rodar(campo, mn, mx, arquivo, nome, passo_padrao=0.15, **kw):
    """atalho para o fim de cada peça: lê passo/--imprimir da linha de comando e esculpe."""
    passo, imp = args(passo_padrao)
    r = esculpir(campo, mn, mx, passo, saida(arquivo, nome, imp), **kw)
    for k, v in r.items():
        print(k, v)
    return r


def pelo(g, comprimento=2.5, fio=0.45, prof=0.22, semente=23):
    """mechas de pelo/pena: ruído esticado na vertical (fios de `fio` mm, `comprimento` mm de mecha)."""
    return prof * ruido_xyz(g.x, g.y, g.z * (fio / comprimento), fio, semente)


def penas(u, v, larg=2.4, alt=2.0, prof=0.3):
    """penas em escama apontando para baixo (u horizontal, v vertical)."""
    return escamas(u, -v, r=larg * 0.6, prof=prof) * 1.0



def normais_d20(rot=None):
    ns = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            for s3 in (-1, 1):
                ns.append((s1, s2, s3))
            ns += [(0, s1 / PHI, s2 * PHI), (s1 / PHI, s2 * PHI, 0), (s1 * PHI, 0, s2 / PHI)]
    ns = np.unique(np.round(np.array(ns, float), 6), axis=0)
    ns /= np.linalg.norm(ns, axis=1)[:, None]
    return ns @ np.array(rot).T if rot is not None else ns


def numeros_d20(g, c, r, rot=None, altura=None, prof=0.6, fonte="sans"):
    """campo dos números 1–20 gravados nas faces de um d20 (faces opostas somam 21). Subtraia do dado com menos()."""
    ns = normais_d20(rot)
    altura = altura or r * 0.42
    usados, num = set(), {}
    k = 1
    for i, n in enumerate(ns):
        if i in usados:
            continue
        j = int(np.argmin(np.linalg.norm(ns + n, axis=1)))
        num[i], num[j] = k, 21 - k
        usados |= {i, j}
        k += 1
    x, y, z = g.p(c)
    d = None
    for i, n in enumerate(ns):
        cima = np.array([0, 0, 1.0]) if abs(n[2]) < 0.9 else np.array([0, 1.0, 0])
        e1 = np.cross(cima, n); e1 /= np.linalg.norm(e1)
        e2 = np.cross(n, e1)
        h = x * n[0] + y * n[1] + z * n[2]
        u = x * e1[0] + y * e1[1] + z * e1[2]
        v = x * e2[0] + y * e2[1] + z * e2[2]
        t = str(num[i]) + ("." if num[i] in (6, 9) else "")
        f = np.maximum(texto2d(u, v, t, altura, fonte), np.abs(h - r) - prof)
        d = f if d is None else np.minimum(d, f)
    return d
