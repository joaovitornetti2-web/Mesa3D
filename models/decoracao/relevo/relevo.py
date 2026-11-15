#!/usr/bin/env python3
"""Profundidade -> placa em arco com baixo-relevo (camafeu): base PRETA, figura BRANCA.
Uso: python3 relevo.py nome  (lê prof/<nome>.npz, grava saida/<nome>_relevo*.stl/3mf)"""
import sys, os
import numpy as np
from scipy import ndimage as ndi
import trimesh, manifold3d as mf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "personagens"))
from triton import LARG_MM, ALT_MM, MOLDURA, arco_dist
from placa import arco

Z_BASE = 1.5        # placa (encaixa 1.28 mm no rebaixo)
H_REL = 3.0         # altura máxima do relevo
Z_COR = Z_BASE + 0.1    # troca de cor logo acima da base: a figura inteira sai branca
FILETE = 0.9


def relevo(nome):
    import json
    meta = json.load(open(f"prof/{nome}.json")); px = meta["px"]
    prof = np.fromfile(f"prof/{nome}.bin", np.float32).reshape(meta["nz"], meta["nx"])
    msk = np.isfinite(prof)
    d = np.where(msk, prof, np.nanmax(prof) if msk.any() else 0)
    D = np.percentile(d[msk], 99) if msk.any() else 1
    base = np.clip(1 - d / D, 0, 1) * msk
    # baixo-relevo: comprime a forma geral e realça o detalhe (passa-alta)
    hp = base - ndi.gaussian_filter(base, 2.2 / px)
    h = 0.55 * base + 1.7 * hp
    h = np.clip(h, 0, None) * msk
    h = ndi.gaussian_filter(h, 0.12 / px)
    h = h / max(np.percentile(h[msk], 99.5), 1e-6) * H_REL if msk.any() else h
    h = np.clip(h, 0, H_REL - 0.25)
    h = np.where(msk, h + 0.25, 0)            # piso de 0.25 mm: nenhuma parte da figura afunda até a base
    h = ndi.gaussian_filter(h, 0.06 / px)      # quina da silhueta levemente suavizada
    nz, nx = h.shape
    dist = arco_dist(nx, nz) * px
    f0, f1, f2 = MOLDURA
    margem = np.clip((dist - f2) / 0.8, 0, 1)            # relevo some suave antes da moldura
    h = h * margem
    h[(dist >= f0) & (dist < f1)] = FILETE              # filete da moldura
    # prévia sombreada (luz de cima-esquerda), cores: preto abaixo da troca, branco acima
    gy, gx = np.gradient(h, px)
    luz = np.clip(0.55 + (-gx * 0.6 + gy * 0.6) / np.sqrt(1 + gx ** 2 + gy ** 2), 0, 1)
    branco = (h > Z_COR - Z_BASE)
    rgb = np.where(branco[..., None], (luz[..., None] * np.array([235, 235, 230])), (0.25 + 0.5 * luz[..., None]) * np.array([40, 40, 42]))
    from PIL import Image
    Image.fromarray(rgb.astype(np.uint8)).save(f"prof/{nome}_previa.png")
    # sólido de altura: topo em grade, fundo plano
    xs = (np.arange(nx) + 0.5) * px * LARG_MM / (nx * px)
    ys = ALT_MM - (np.arange(nz) + 0.5) * px * ALT_MM / (nz * px)
    X, Y = np.meshgrid(xs, ys)
    top = np.c_[X.ravel(), Y.ravel(), (Z_BASE + h).ravel()]
    bot = np.c_[X.ravel(), Y.ravel(), np.zeros(X.size)]
    V = np.vstack([top, bot]); n = X.size
    idx = np.arange(n).reshape(nz, nx)
    a, b, c, e = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel()
    F = [np.c_[a, c, b], np.c_[b, c, e], np.c_[a + n, b + n, c + n], np.c_[b + n, e + n, c + n]]
    for borda in (idx[0, :], idx[:, -1], idx[-1, ::-1], idx[::-1, 0]):
        p, q = borda[:-1], borda[1:]
        F += [np.c_[p, q, p + n], np.c_[q, q + n, p + n]]
    T = trimesh.Trimesh(V, np.vstack(F), process=True)
    if T.volume < 0: T.invert()
    S = mf.Manifold(mf.Mesh(vert_properties=np.asarray(T.vertices, np.float32), tri_verts=np.asarray(T.faces, np.uint32)))
    A = arco().offset(-0.01, mf.JoinType.Miter).extrude(Z_BASE + H_REL + 2).translate((0, 0, -0.5))
    P = S ^ A
    cima = P.trim_by_plane((0, 0, 1), Z_COR)
    baixo = P.trim_by_plane((0, 0, -1), -Z_COR)

    def tm(m):
        g = m.to_mesh()
        return trimesh.Trimesh(np.asarray(g.vert_properties)[:, :3], np.asarray(g.tri_verts), process=False)

    os.makedirs("saida", exist_ok=True)
    tm(P).export(f"saida/{nome}_relevo.stl")
    cena = trimesh.Scene()
    for k, (m, cor) in enumerate([(baixo, "preto"), (cima, "branco")], 1):
        t = tm(m); t.export(f"saida/{nome}_relevo_cor{k}.stl")
        cena.add_geometry(t, node_name=f"{nome}_cor{k}_{cor}", geom_name=f"{nome}_cor{k}_{cor}")
    cena.export(f"saida/{nome}_relevo_2cores.3mf")
    ok = trimesh.load(f"saida/{nome}_relevo.stl").is_watertight
    print(nome, tm(P).extents.round(1), "fechada", ok)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        relevo(n)
