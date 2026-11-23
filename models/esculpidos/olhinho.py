"""Olhinho – o vigia desconfiado: pálpebra meio fechada, veinhas, asas de morcego e chifrinhos.
c1 pálpebra/asas/pernas/base · c2 pupila · c3 branco do olho e brilho · c4 íris, veinhas e pedrinha da base."""
import sys
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2
g = Grade((-34, -22, 0), (34, 24, 52), passo)
X, Y, Z = g.x, g.y, g.z
OZ, OR = 27.0, 14.0

olho = esfera(g, (0, 0, OZ), OR)
# pálpebra de cima, caída e torta (cara de "eu vi isso")
palp = np.maximum(esfera(g, (0, 0.6, OZ + 0.2), OR + 1.3), -(Z - (OZ + 4.6) - 0.14 * X - 0.12 * (Y + OR)))
palp = smin(palp, np.maximum(esfera(g, (0, 0.6, OZ), OR + 1.1), Z - (OZ - 8.5) + 0.0 * X), 0.1) if False else palp
borda = np.maximum(toro(Vista(g, (0, 0, OZ + 4.2), mul(rot_y(-8), rot_x(-7))), (0, 0, OZ + 4.2), OR - 0.2, 1.15), -esfera(g, (0, 0, OZ), OR - 3))
palp = smin(palp, np.maximum(borda, -(Z - OZ + 4)), 0.6)
# pálpebra de baixo fininha
palp_b = np.maximum(esfera(g, (0, 0.3, OZ), OR + 0.8), Z - (OZ - 8.2) - 0.1 * X)
corpo = smin(olho, palp, 0.4)

# chifrinhos curvos saindo da pálpebra
for s in (-1, 1):
    corpo = smin(corpo, tubo(g, [(s * 7, 2, OZ + 11.5), (s * 10, 3, OZ + 16), (s * 9.5, 5, OZ + 19.5), (s * 7.5, 6, OZ + 20.5)],
                             [3.0, 2.2, 1.3, 0.5]), 1.5)

# asas de morcego (membrana com recortes + ossinhos)
for s in (-1, 1):
    c = (s * 12.5, 4.5, OZ + 1)
    v = Vista(g, c, mul(rot_z(s * -18), rot_y(s * -12)))
    lx, ly, lz = (v.x - c[0]) * s, v.y - c[1], v.z - c[2]
    memb = elipsoide(v, (c[0] + s * 10, c[1], c[2] + 2), (11, 6, 9))
    memb = np.maximum(memb, np.abs(ly) - 0.85)
    memb = np.maximum(memb, -lx + 0.5)
    for k in range(3):                               # recortes da borda de baixo
        cx = c[0] + s * (6 + k * 5.5)
        memb = menos(memb, esfera(v, (cx, c[1], c[2] - 7.8 + k * 1.8), 3.6), 0.4)
    ossos = None
    for (bx, bz) in ((17, 7), (17, 0.5)):
        o = capsula(v, (c[0], c[1], c[2] + 3), (c[0] + s * bx, c[1], c[2] + bz), 1.5, 0.6)
        ossos = o if ossos is None else np.minimum(ossos, o)
    asa = smin(memb, ossos, 0.6)
    corpo = smin(corpo, asa, 1.6)

# perninhas com três dedinhos sobre uma pedrinha
pedra = elipsoide(g, (0, 1, 2.6), (13, 10, 4.2))
pedra = pedra + 0.35 * ruido(g, 1.4, 11)
pedra = np.maximum(pedra, -Z)
for s in (-1, 1):
    corpo = smin(corpo, tubo(g, [(s * 5, 1, OZ - 11), (s * 6.5, 0, 12), (s * 6, -1, 6.4)], [2.6, 2.0, 1.9]), 1.5)
    for d in (-1, 0, 1):
        corpo = smin(corpo, capsula(g, (s * 6, -1, 6.4), (s * 6 + d * 2.2, -4.2, 5.8), 1.2, 0.9), 0.6)
corpo = smin(corpo, pedra, 1.0)
corpo = np.maximum(corpo, -Z)

# íris olhando de lado (desconfiado), pupila, brilho e veinhas no branco
ax = np.array([-0.18, -1.0, -0.02]); ax /= np.linalg.norm(ax)
cen = np.array([0, 0, OZ])
def ao_longo(r):
    x, y, z = g.p(tuple(cen))
    t = x * ax[0] + y * ax[1] + z * ax[2]
    rr = np.sqrt(np.maximum(x * x + y * y + z * z - t * t, 0))
    return np.maximum(rr - r, -(t - 4))
iris = ao_longo(6.2)
pupila = ao_longo(2.9)
pc = cen + ax * OR
brilho = esfera(g, tuple(pc + np.array([1.8, -0.3, 2.0])), 1.1)
corpo = smin(corpo, brilho, 0.3)
veias = None
rng = np.random.default_rng(2)
for k in range(7):
    a0 = rng.uniform(-2.6, -0.5) if k % 2 else rng.uniform(-np.pi + 0.3, -2.4)
    e0 = rng.uniform(-0.6, 0.15)
    pts = []
    for i in range(4):
        a, e = a0 + i * 0.22 * (1 if k % 2 else -1), e0 + i * 0.09 * np.sin(k + i)
        pts.append((OR * np.cos(e) * np.cos(a), OR * np.cos(e) * np.sin(a), OZ + OR * np.sin(e)))
    vv = tubo(g, pts, [0.6, 0.5, 0.4, 0.25])
    veias = vv if veias is None else np.minimum(veias, vv)
veias = np.maximum(veias, -ao_longo(6.6))

branco = np.maximum(esfera(g, (0, 0, OZ), OR + 0.25), -(palp - 0.05))
branco = np.maximum(branco, -iris)
reg = {"c2": pupila, "c3": np.minimum(np.maximum(branco, -veias), brilho - 0.05), "c4": np.minimum.reduce([iris, veias])}
for k, v_ in exportar(g, dividir(corpo, reg), "stl/olhinho", faces=300000).items():
    print(k, v_)
