"""Biblioteca de figura humana para miniaturas de mesa (escala heroica 28–32 mm, base de 25 mm).

Unidades em mm. A figura fica de pé com os pés em z = BASE (topo da base), de frente para −y.
Fluxo de uma miniatura:
    J = esqueleto("f", mao_d=(...), cotovelo_d=(...))     # pose (pontos absolutos, opcionais)
    b = corpo(g, J)                                       # corpo nu (campo)
    cab = cabeca(g, J, cabelo="rabo")                     # cabeça com rosto e cabelo
    roupa = camisa(g, J, b) ...                           # camadas que acompanham o corpo
    arma = espada(g, J["mao_d"], direcao, ...)            # equipamentos
O campo final é a união; a peça chama esculpir() do kit de detalhe.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *  # noqa: F401,F403

BASE = 3.0                       # altura da base redonda


# ------------------------------------------------------------------ esqueleto
def esqueleto(sexo="m", escala=1.0, **pose):
    """juntas da figura em pé, braços soltos. `pose` substitui qualquer junta (coordenadas absolutas):
    ombro_e/d, cotovelo_e/d, mao_e/d, quadril_e/d, joelho_e/d, pe_e/d, cabeca, peito, pelve, giro (graus no z
    do tronco), inclina (graus para a frente)."""
    f = sexo == "f"
    s = escala * (0.96 if f else 1.0)
    z = lambda v: BASE + v * s
    om = 3.9 if f else 4.6                       # meia largura dos ombros
    qd = 2.25 if f else 2.0                      # meia largura do quadril
    J = {
        "sexo": sexo, "s": s,
        "pelve": (0, 0.2, z(17.4)), "cintura": (0, 0.1, z(20.2)), "peito": (0, 0, z(24.2)),
        "pescoco": (0, 0.1, z(28.4)), "cabeca": (0, -0.1, z(31.1)),
        "ombro_e": (-om * s, 0.2, z(26.6)), "ombro_d": (om * s, 0.2, z(26.6)),
        "quadril_e": (-qd * s, 0.2, z(17.0)), "quadril_d": (qd * s, 0.2, z(17.0)),
    }
    for lado, sx in (("e", -1), ("d", 1)):
        o = J["ombro_" + lado]
        J["cotovelo_" + lado] = (o[0] + sx * 0.9 * s, o[1] + 0.3 * s, o[2] - 5.6 * s)
        J["mao_" + lado] = (o[0] + sx * 1.3 * s, o[1] - 0.4 * s, o[2] - 10.6 * s)
        q = J["quadril_" + lado]
        J["pe_" + lado] = (q[0] + sx * 0.5 * s, q[1] - 0.2, BASE + 0.9 * s)
    J.update(pose)
    for lado in ("e", "d"):                      # joelho entre quadril e pé, um pouco à frente
        if "joelho_" + lado not in pose:
            q, p = np.array(J["quadril_" + lado]), np.array(J["pe_" + lado])
            m = (q + p) / 2
            J["joelho_" + lado] = (m[0], m[1] - 0.5 * s, m[2] + 0.4 * s)
    return J


def _v(a):
    return np.array(a, float)


# ------------------------------------------------------------------ corpo
def corpo(g, J, musculo=1.0, peso=1.0):
    """corpo nu (sem cabeça): tronco, pescoço, braços, mãos, pernas e pés."""
    f, s = J["sexo"] == "f", J["s"]
    p, c, pe, ci = J["pelve"], J["peito"], J["pescoco"], J["cintura"]
    larg_p = (3.4 if f else 3.9) * s * musculo
    torax = elipsoide(g, (c[0], c[1], c[2] + 0.3 * s), (larg_p, (2.4 if f else 2.7) * s * peso, 3.9 * s))
    cint = elipsoide(g, ci, ((2.5 if f else 2.9) * s * peso, 1.9 * s * peso, 2.4 * s))
    pelv = elipsoide(g, p, ((3.3 if f else 2.9) * s * peso, 2.1 * s * peso, 2.4 * s))
    b = smin(smin(torax, cint, 1.4 * s), pelv, 1.4 * s)
    if f:
        for sx in (-1, 1):
            b = smin(b, esfera(g, (c[0] + sx * 1.35 * s, c[1] - 1.6 * s, c[2] - 0.4 * s), 1.35 * s), 0.6 * s)
    else:
        for sx in (-1, 1):                                               # peitoral
            b = smin(b, elipsoide(g, (c[0] + sx * 1.6 * s, c[1] - 1.4 * s, c[2] + 0.2 * s), (1.7 * s, 1.0 * s, 1.3 * s)), 0.7 * s)
    b = smin(b, capsula(g, pe, (pe[0], pe[1], pe[2] - 2.2 * s), 1.15 * s), 0.8 * s)   # pescoço
    oe, od = J["ombro_e"], J["ombro_d"]
    b = smin(b, capsula(g, (oe[0] * 0.7, oe[1] + 0.2 * s, oe[2] + 0.3 * s), (od[0] * 0.7, od[1] + 0.2 * s, od[2] + 0.3 * s), (1.15 if f else 1.35) * s * musculo), 1.3 * s)   # trapézio e clavículas
    for lado in ("e", "d"):
        o, co, m = J["ombro_" + lado], J["cotovelo_" + lado], J["mao_" + lado]
        b = smin(b, esfera(g, o, (1.35 if f else 1.55) * s * musculo), 1.0 * s)        # deltoide
        b = smin(b, tubo(g, [o, co, m], [(1.1 if f else 1.3) * s * musculo, (0.9 if f else 1.0) * s, 0.72 * s]), 0.6 * s)
        b = smin(b, mao(g, co, m, s), 0.25 * s)
        q, j, pp = J["quadril_" + lado], J["joelho_" + lado], J["pe_" + lado]
        b = smin(b, tubo(g, [q, j, pp], [(2.1 if f else 2.0) * s * peso, 1.3 * s, 0.9 * s]), 0.9 * s)
        meio = (np.array(j) + np.array(pp)) / 2 + np.array([0, 0.35 * s, 0.6 * s])
        b = smin(b, esfera(g, tuple(meio), 1.25 * s), 0.8 * s)                           # panturrilha
        b = smin(b, pe_(g, pp, s), 0.3 * s)
    return b


def mao(g, cotovelo, m, s):
    """mão fechada (punho) no fim do antebraço: segura cabos que passam por `m`."""
    d = _v(m) - _v(cotovelo)
    d = d / np.linalg.norm(d)
    c = _v(m) + d * 0.55 * s
    return smin(esfera(g, tuple(c), 0.82 * s), esfera(g, tuple(c + d * 0.4 * s), 0.7 * s), 0.3 * s)


def pe_(g, pp, s):
    x, y, z = pp
    return smin(elipsoide(g, (x, y - 1.0 * s, BASE + 0.55 * s), (0.85 * s, 1.85 * s, 0.6 * s)),
                esfera(g, (x, y + 0.3 * s, BASE + 0.8 * s), 0.8 * s), 0.4 * s)


# ------------------------------------------------------------------ cabeça, rosto e cabelo
def cabeca(g, J, cabelo="curto", barba=None, expressao="seria", olhar=0.0):
    """cabeça com rosto (testa, olhos fundos, nariz, boca, queixo, orelhas) e cabelo.
    cabelo: careca, raspado, curto, topete, longo, rabo, coque, trancas, moicano. barba: None, cavanhaque, cheia."""
    f, s = J["sexo"] == "f", J["s"] * 1.12
    cx, cy, cz = J["cabeca"]
    gv = Vista(g, (cx, cy, cz), rot_z(olhar)) if olhar else g
    cr = elipsoide(gv, (cx, cy + 0.15 * s, cz + 0.25 * s), (1.95 * s, 2.25 * s, 2.25 * s))
    rosto = elipsoide(gv, (cx, cy - 0.8 * s, cz - 0.6 * s), ((1.55 if f else 1.7) * s, 1.6 * s, 1.9 * s))
    h = smin(cr, rosto, 0.8 * s)
    queixo = esfera(gv, (cx, cy - 1.55 * s, cz - 2.05 * s), (0.55 if f else 0.75) * s)
    h = smin(h, queixo, 0.6 * s)
    if not f:
        for sx in (-1, 1):                                                   # mandíbula marcada
            h = smin(h, esfera(gv, (cx + sx * 1.15 * s, cy - 0.6 * s, cz - 1.5 * s), 0.6 * s), 0.6 * s)
    # testa/sobrancelha, olhos fundos, maçãs, nariz, lábios
    h = smin(h, capsula(gv, (cx - 1.05 * s, cy - 1.85 * s, cz + 0.45 * s), (cx + 1.05 * s, cy - 1.85 * s, cz + 0.45 * s), 0.32 * s), 0.35 * s)
    for sx in (-1, 1):
        h = menos(h, esfera(gv, (cx + sx * 0.72 * s, cy - 2.0 * s, cz + 0.05 * s), 0.33 * s), 0.2 * s)
        h = np.minimum(h, elipsoide(gv, (cx + sx * 0.72 * s, cy - 1.8 * s, cz + 0.02 * s), (0.3 * s, 0.22 * s, 0.17 * s)))   # globo/pálpebra
        h = smin(h, capsula(gv, (cx + sx * 0.3 * s, cy - 2.12 * s, cz + 0.55 * s), (cx + sx * 1.2 * s, cy - 1.95 * s, cz + (0.5 if f else 0.42) * s), (0.1 if f else 0.16) * s), 0.1 * s)   # sobrancelha
        h = smin(h, esfera(gv, (cx + sx * 1.0 * s, cy - 1.55 * s, cz - 0.55 * s), 0.45 * s), 0.4 * s)     # maçã
        h = smin(h, elipsoide(gv, (cx + sx * 1.95 * s, cy + 0.05 * s, cz - 0.15 * s), (0.25 * s, 0.45 * s, 0.65 * s)), 0.2 * s)  # orelha
    h = smin(h, capsula(gv, (cx, cy - 2.0 * s, cz + 0.05 * s), (cx, cy - 2.35 * s, cz - 0.8 * s), 0.22 * s, 0.32 * s), 0.25 * s)  # nariz
    boca_z = cz - 1.35 * s
    labio = capsula(gv, (cx - 0.45 * s, cy - 1.92 * s, boca_z), (cx + 0.45 * s, cy - 1.92 * s, boca_z), (0.17 if f else 0.13) * s)
    h = smin(h, labio, 0.12 * s)
    zb = boca_z + ((0.22 * s * ((gv.x - cx) / (0.5 * s)) ** 2 - 0.08 * s) if expressao == "sorriso" else 0)
    fenda = np.maximum(np.abs(gv.z - zb) - 0.05 * s, np.maximum(np.abs(gv.x - cx) - 0.45 * s, -(gv.y - cy + 2.4 * s)))
    if expressao == "grito":
        fenda = elipsoide(gv, (cx, cy - 1.95 * s, boca_z - 0.15 * s), (0.4 * s, 0.4 * s, 0.35 * s))
    h = menos(h, fenda, 0.05 * s)
    h = h + 0.012 * ruido_cel(gv, 0.25, 7)
    # cabelo
    ca = _cabelo(gv, (cx, cy, cz), s, cabelo, f)
    if barba:
        bb = elipsoide(gv, (cx, cy - 1.15 * s, cz - 1.55 * s), (1.6 * s, 1.15 * s, 1.15 * s)) if barba == "cheia" else \
            elipsoide(gv, (cx, cy - 1.75 * s, cz - 2.0 * s), (0.6 * s, 0.6 * s, 0.75 * s))
        bb = np.maximum(bb, -(gv.y - cy + 2.6 * s))
        bb = menos(bb, elipsoide(gv, (cx, cy - 2.0 * s, boca_z), (0.55 * s, 0.6 * s, 0.25 * s)), 0.05 * s)
        bb = bb + 0.06 * s * np.abs(np.sin((gv.x - cx) * 9 / s))
        ca = bb if ca is None else np.minimum(ca, bb)
    return h, ca


def _cabelo(g, c, s, tipo, f):
    cx, cy, cz = c
    if tipo == "careca":
        return None
    cr = elipsoide(g, (cx, cy + 0.25 * s, cz + 0.4 * s), (2.3 * s, 2.6 * s, 2.6 * s))
    alto = np.maximum(cr, np.maximum(cz + 0.6 * s - g.z, -(g.y - cy + 1.9 * s)))                  # calota acima da testa
    nuca = np.maximum(cr, np.maximum(cz - 1.0 * s - g.z, -(g.y - cy - 0.5 * s)))                   # atrás, até a nuca
    franja = np.maximum(cr, np.maximum(cz + 0.95 * s - 0.35 * s * np.cos((g.x - cx) * 1.6 / s) - g.z, g.y - cy + 1.0 * s))
    base = np.minimum(np.minimum(alto, nuca), franja)
    if tipo == "raspado":
        return np.maximum(base, -(cr + 0.22 * s))
    mechas = 0.12 * s * np.abs(np.sin(np.arctan2(g.x - cx, g.y - cy) * 16 + (g.z - cz) * 1.5 / s))
    if tipo in ("curto", "topete", "moicano"):
        d = base + mechas
        if tipo == "topete":
            d = smin(d, elipsoide(g, (cx, cy - 1.0 * s, cz + 2.3 * s), (1.5 * s, 1.4 * s, 0.9 * s)), 0.5 * s)
        if tipo == "moicano":
            d = np.maximum(d, -(cr + 0.1 * s))
            d = np.minimum(np.maximum(d, np.abs(g.x - cx) - 2.5 * s), np.maximum(elipsoide(g, (cx, cy + 0.2 * s, cz + 1.4 * s), (0.5 * s, 2.6 * s, 2.0 * s)), -(g.z - cz - 0.2 * s)))
            d = np.minimum(d, np.maximum(base, -(cr + 0.1 * s)))
        return d
    # longos: caem pelas costas até os ombros
    cai = capsula(g, (cx, cy + 1.0 * s, cz), (cx, cy + 1.3 * s, cz - (5.0 if tipo == "longo" else 2.5) * s), 2.0 * s, 1.6 * s)
    cai = np.maximum(cai, -(g.y - cy - 0.3 * s))
    d = smin(base, cai, 0.8 * s) + mechas
    if tipo == "longo":
        for sx in (-1, 1):                                                    # mechas na frente dos ombros
            d = smin(d, capsula(g, (cx + sx * 1.8 * s, cy - 0.4 * s, cz - 0.5 * s), (cx + sx * 2.1 * s, cy - 0.2 * s, cz - 4.0 * s), 0.55 * s, 0.4 * s), 0.4 * s)
    elif tipo == "rabo":
        d = base + mechas
        d = smin(d, tubo(g, [(cx, cy + 2.2 * s, cz + 0.8 * s), (cx, cy + 3.1 * s, cz - 0.6 * s), (cx, cy + 2.8 * s, cz - 3.6 * s)], [0.75 * s, 0.6 * s, 0.25 * s]), 0.4 * s)
    elif tipo == "coque":
        d = smin(base + mechas, esfera(g, (cx, cy + 1.9 * s, cz + 1.6 * s), 1.05 * s), 0.4 * s)
    elif tipo == "trancas":
        d = base + mechas
        for sx in (-1, 1):
            pts = [(cx + sx * 1.7 * s, cy + 0.6 * s, cz - 0.6 * s), (cx + sx * 2.0 * s, cy + 0.2 * s, cz - 2.5 * s), (cx + sx * 1.9 * s, cy - 0.3 * s, cz - 4.6 * s)]
            t = tubo(g, pts, [0.55 * s, 0.5 * s, 0.4 * s])
            t = t + 0.12 * s * np.abs(np.sin(g.z * 5 / s))
            d = smin(d, t, 0.3 * s)
    return d


# ------------------------------------------------------------------ roupas (acompanham o corpo b)
def faixa_z(g, z0, z1):
    return np.maximum(z0 - g.z, g.z - z1)


def vincos(g, J, prof=0.14):
    """rugas de pano nas dobras: anéis em volta dos cotovelos e joelhos, e na parte de trás do joelho."""
    s = J["s"]
    d = 0
    for lado in ("e", "d"):
        for j in ("cotovelo_", "joelho_"):
            c = _v(J[j + lado])
            r = np.sqrt((g.x - c[0]) ** 2 + (g.y - c[1]) ** 2 + (g.z - c[2]) ** 2)
            d = d + prof * s * np.clip(1 - r / (2.2 * s), 0, 1) * np.abs(np.sin((g.z - c[2]) * 3.2 / s + (g.x - c[0]) * 1.1 / s))
    return d


def camada(b, esp, regiao):
    """roupa justa: o corpo inchado de `esp` só dentro da `regiao` (campo < 0 dentro)."""
    return np.maximum(b - esp, regiao)


def dobras(g, eixo_xy=(0, 0), n=9, prof=0.12, fase=0.0):
    """dobras verticais de pano em volta de um eixo."""
    return prof * np.abs(np.sin(np.arctan2(g.y - eixo_xy[1], g.x - eixo_xy[0]) * n + fase + 0.4 * np.sin(g.z * 0.7)))


def manto(g, J, z_topo, r_topo, r_chao, aberto_frente=0.0, rasgado=False, n_dobras=11):
    """túnica/vestido/manto em sino do quadril (ou ombro) até o chão."""
    s = J["s"]
    p = J["pelve"]
    t = np.clip((z_topo - g.z) / max(z_topo - BASE, 1), 0, 1)
    r = r_topo + (r_chao - r_topo) * t ** 0.8
    rad = np.sqrt(((g.x - p[0]) / 1.0) ** 2 + ((g.y - p[1]) / 0.82) ** 2)
    d = np.maximum(rad - r, np.maximum(BASE + 0.2 - g.z, g.z - z_topo))
    d = d + dobras(g, (p[0], p[1]), n_dobras, 0.22 * s) * t
    if aberto_frente:
        d = menos(d, np.maximum(np.abs(g.x - p[0]) - aberto_frente * t, -(g.y - p[1] + 0.5)), 0.3 * s)
    if rasgado:
        barra = BASE + 0.3 + 1.2 * s * np.clip(ruido_cel(g, 1.4, 31), 0, None)
        d = np.maximum(d, barra - g.z)
    return d


def capa(g, J, comp=1.0, larg=1.0, vento=0.0, capuz=False):
    """capa presa nos ombros caindo pelas costas (com volume e dobras)."""
    s = J["s"]
    oe, od = J["ombro_e"], J["ombro_d"]
    zt = oe[2] + 0.6 * s
    zb = BASE + 0.4 + (1 - comp) * 12 * s
    t = np.clip((zt - g.z) / (zt - zb), 0, 1)
    meia = (abs(od[0]) + 0.9 * s) * (1 + 0.55 * t) * larg
    yb = 1.6 * s + 3.5 * s * t ** 1.4 * (1 + vento)
    atras = np.abs(g.y - 0.3 * s - yb * 0.5) - (0.6 * s + yb * 0.5)
    casca = np.maximum(np.abs(g.x) - meia, np.maximum(-(g.y - 1.2 * s - 1.6 * s * t), atras))
    d = np.maximum(casca, np.maximum(zb - g.z, g.z - zt))
    d = np.maximum(d, -(np.sqrt(g.x ** 2 + ((g.y - 0.2) * 1.4) ** 2) - 3.0 * s) * (g.z > zt - 1.5 * s))       # gola em volta do pescoço
    d = d + 0.28 * s * np.abs(np.sin(g.x * 1.3 / s + 0.5)) * t
    if capuz:
        h = J["cabeca"]
        cap = np.maximum(np.abs(elipsoide(g, (h[0], h[1] + 0.9 * s, h[2] - 0.2 * s), (2.6 * s, 2.7 * s, 2.7 * s))) - 0.28 * s, -(g.y - h[1] + 0.4 * s))
        d = smin(d, np.maximum(cap, h[2] - 3.0 * s - g.z), 0.4 * s)
    return d


def capuz_vestido(g, J):
    """capuz levantado cobrindo a cabeça (rosto na sombra)."""
    s = J["s"]
    h = J["cabeca"]
    cap = np.abs(elipsoide(g, (h[0], h[1] + 0.5 * s, h[2] + 0.2 * s), (2.65 * s, 2.9 * s, 2.85 * s))) - 0.3 * s
    cap = np.maximum(cap, -(g.y - h[1] + 2.3 * s - 0.6 * s * np.clip((h[2] + 2.5 * s - g.z) / (4 * s), 0, 1)))
    cap = smin(cap, capsula(g, (h[0], h[1] + 2.6 * s, h[2] + 2.4 * s), (h[0], h[1] + 3.6 * s, h[2] + 1.0 * s), 0.6 * s, 0.25 * s), 0.4 * s)
    return np.maximum(cap, h[2] - 3.4 * s - g.z)


def cinto(g, J, z=None, esp=0.35, fivela=True):
    s = J["s"]
    p = J["pelve"]
    z = z if z is not None else p[2] + 1.3 * s
    d = np.maximum(np.abs(np.sqrt(((g.x - p[0]) / 1.0) ** 2 + ((g.y - p[1]) / 0.72) ** 2) - (2.95 if J["sexo"] == "m" else 3.0) * s) - esp * s, np.abs(g.z - z) - 0.45 * s)
    if fivela:
        d = np.minimum(d, caixa(g, (p[0], p[1] - 2.2 * s, z), (0.55 * s, 0.25 * s, 0.5 * s), 0.12 * s))
    return d


def botas(g, J, b, alto=7.5, esp=0.28):
    s = J["s"]
    d = camada(b, esp * s, faixa_z(g, BASE - 1, BASE + alto * s))
    for lado in ("e", "d"):                                                   # dobra do cano
        pp = J["pe_" + lado]
        d = smin(d, np.maximum(capsula(g, (pp[0], pp[1] + 0.2 * s, BASE + alto * s - 0.4 * s), (pp[0], pp[1] + 0.2 * s, BASE + alto * s), 1.2 * s), -g.z), 0.2 * s)
    return d


def ombreira(g, J, lado, r=1.9, camadas=2):
    s = J["s"]
    o = _v(J["ombro_" + lado])
    sx = -1 if lado == "e" else 1
    d = None
    for k in range(camadas):
        c = o + np.array([sx * (0.4 + 0.25 * k) * s, 0, (0.6 - 0.9 * k) * s])
        e = np.maximum(np.abs(esfera(g, tuple(c), (r - 0.15 * k) * s)) - 0.3 * s, -(g.z - c[2] + 0.9 * s))
        d = e if d is None else np.minimum(d, e)
    return d


def peitoral(g, J, b, esp=0.55, z0=None, z1=None, placas=True):
    """couraça de metal: o tronco inchado, com borda e linha central."""
    s = J["s"]
    z0 = z0 if z0 is not None else J["pelve"][2] + 0.5 * s
    z1 = z1 if z1 is not None else J["ombro_e"][2] + 0.4 * s
    regiao = np.maximum(faixa_z(g, z0, z1), np.abs(g.x) - (abs(J["ombro_d"][0]) + 0.2 * s))
    regiao = np.maximum(regiao, -(np.sqrt(g.x ** 2 + ((g.y - 0.2) * 1.3) ** 2) - 1.6 * s) * (g.z > z1 - 1.2 * s))   # gola
    d = camada(b, esp * s, regiao)
    if placas:                                                                  # faixas articuladas na barriga
        for k in range(3):
            zz = z0 + (0.9 + 1.1 * k) * s
            d = menos(d, np.maximum(np.abs(g.z - zz) - 0.08 * s, -(d + 0.18 * s)), 0.05 * s)
        d = smin(d, np.maximum(capsula(g, (0, -3.0 * s, z1 - 0.5 * s), (0, -3.0 * s, z0 + 4.0 * s), 0.2 * s), d - 0.25 * s), 0.1 * s)   # quilha
    return d


def calca(g, J, b, esp=0.22, folgada=0.0):
    s = J["s"]
    d = camada(b, (esp + folgada) * s, np.maximum(faixa_z(g, BASE + 0.8 * s, J["pelve"][2] + 1.0 * s), np.abs(g.x) - 4.6 * s))
    return d + 0.05 * s * np.abs(np.sin(g.z * 2.2 / s + g.x))


def camisa(g, J, b, esp=0.2, manga=1.0, gola=True):
    """camisa/casaco: tronco e braços até `manga` (0 = sem manga, 1 = até o pulso)."""
    s = J["s"]
    tronco = np.maximum(faixa_z(g, J["pelve"][2] - 0.8 * s, J["pescoco"][2] - 0.9 * s), np.abs(g.x) - (abs(J["ombro_d"][0]) + 1.4 * s))
    regiao = tronco
    if manga > 0:
        for lado in ("e", "d"):
            o, co, m = _v(J["ombro_" + lado]), _v(J["cotovelo_" + lado]), _v(J["mao_" + lado])
            fim = co + (m - co) * min(1.0, manga * 2 - 1) if manga > 0.5 else o + (co - o) * manga * 2
            meio = co if manga > 0.5 else fim
            br = tubo(g, [tuple(o), tuple(meio), tuple(fim)], [2.0 * s, 1.6 * s, 1.3 * s]) if manga > 0.5 else capsula(g, tuple(o), tuple(fim), 1.9 * s)
            regiao = np.minimum(regiao, br)
    d = camada(b, esp * s, regiao)
    if gola:
        pe = J["pescoco"]
        d = smin(d, np.maximum(np.abs(np.sqrt((g.x - pe[0]) ** 2 + ((g.y - pe[1]) * 1.1) ** 2) - 1.45 * s) - 0.2 * s, np.abs(g.z - pe[2] + 0.9 * s) - 0.45 * s), 0.2 * s)
    return d + 0.05 * s * np.abs(np.sin(g.z * 1.7 / s + 0.3 * g.x))


def jaqueta(g, J, b, comp=1.0, aberta=True, esp=0.42):
    """jaqueta/sobretudo aberto na frente, com lapela; comp > 1 desce como sobretudo até o joelho."""
    s = J["s"]
    zb = J["pelve"][2] - 1.2 * s - max(0, comp - 1) * 9 * s
    d = camisa(g, J, b, esp=esp, manga=1.0, gola=False)
    if comp > 1:
        aba = manto(g, J, J["pelve"][2] + 0.5 * s, 3.6 * s, 4.4 * s, aberto_frente=1.6 * s, n_dobras=7)
        d = smin(d, np.maximum(aba, zb - g.z), 0.3 * s)
    d = np.maximum(d, zb - g.z)
    if aberta:
        d = menos(d, np.maximum(np.abs(g.x) - 0.55 * s - 0.5 * s * np.clip((J["peito"][2] - g.z) / (6 * s), 0, 1), np.maximum(-(g.y + 1.0 * s), J["peito"][2] + 2.6 * s - g.z)), 0.1 * s)
        for sx in (-1, 1):                                                       # lapelas
            d = smin(d, np.maximum(capsula(g, (sx * 0.9 * s, -2.6 * s, J["peito"][2] + 2.6 * s), (sx * 1.6 * s, -2.9 * s, J["peito"][2] - 0.6 * s), 0.35 * s), -g.z), 0.15 * s)
    return d


def colete(g, J, b, esp=0.7, bolsos=True):
    """colete tático: tronco grosso com bolsos na frente."""
    s = J["s"]
    regiao = np.maximum(faixa_z(g, J["pelve"][2] + 0.8 * s, J["ombro_e"][2] + 0.2 * s), np.abs(g.x) - (abs(J["ombro_d"][0]) - 0.3 * s))
    d = camada(b, esp * s, regiao)
    if bolsos:
        yf = J["cintura"][1] - (2.25 + esp + 0.3) * s                                 # frente do colete na cintura
        for sx in (-1.7, 0, 1.7):
            d = np.minimum(d, caixa(g, (sx * s, yf, J["cintura"][2] + 0.1 * s), (0.72 * s, 0.5 * s, 0.95 * s), 0.18 * s))
            d = np.minimum(d, caixa(g, (sx * s, yf - 0.15 * s, J["cintura"][2] + 0.95 * s), (0.78 * s, 0.45 * s, 0.22 * s), 0.1 * s))   # aba
        yp = J["peito"][1] - (2.8 + esp + 0.25) * s
        for sx in (-1, 1):
            d = np.minimum(d, caixa(g, (sx * 1.7 * s, yp, J["peito"][2] + 0.4 * s), (0.75 * s, 0.45 * s, 0.75 * s), 0.18 * s))
    return d


def bolsa_lateral(g, J, lado="d", tam=1.0):
    s = J["s"]
    q = J["quadril_" + lado]
    sx = -1 if lado == "e" else 1
    return caixa(g, (q[0] + sx * 1.9 * s, q[1], q[2] + 0.3 * s), (0.6 * s * tam, 1.0 * s * tam, 1.1 * s * tam), 0.3 * s)


def mochila(g, J, tam=1.0):
    s = J["s"]
    c = J["peito"]
    d = caixa(g, (c[0], c[1] + 3.2 * s, c[2] - 0.5 * s), (2.3 * s * tam, 1.1 * s * tam, 2.8 * s * tam), 0.7 * s)
    d = smin(d, caixa(g, (c[0], c[1] + 4.3 * s, c[2] - 1.8 * s), (1.6 * s, 0.45 * s, 1.1 * s), 0.3 * s), 0.2 * s)
    return d


# ------------------------------------------------------------------ equipamentos (pontos absolutos)
def _frame(dirv):
    z_ = _v(dirv) / np.linalg.norm(dirv)
    a = np.array([0, 0, 1.0]) if abs(z_[2]) < 0.9 else np.array([1.0, 0, 0])
    x_ = np.cross(a, z_); x_ /= np.linalg.norm(x_)
    return x_, np.cross(z_, x_), z_


def _local(g, origem, dirv, plano=None):
    """coordenadas locais (u, v, w): w ao longo de dirv; u na direção de `plano` (projetada)."""
    x_, y_, z_ = _frame(dirv)
    if plano is not None:
        p = _v(plano) - z_ * (_v(plano) @ z_)
        if np.linalg.norm(p) > 1e-6:
            x_ = p / np.linalg.norm(p); y_ = np.cross(z_, x_)
    X, Y, Z = g.x - origem[0], g.y - origem[1], g.z - origem[2]
    return (X * x_[0] + Y * x_[1] + Z * x_[2], X * y_[0] + Y * y_[1] + Z * y_[2], X * z_[0] + Y * z_[1] + Z * z_[2])


def espada(g, mao_, dirv, comp=13.0, larg=1.0, plano=(1, 0, 0), cabo=2.6):
    """espada: lâmina com sulco, guarda e pomo; empunhada em mao_ apontando para dirv."""
    u, v, w = _local(g, mao_, dirv, plano)
    lam = np.maximum(np.maximum(np.abs(u) - larg * 0.5 * np.clip((comp - w) / 1.6, 0.05, 1), np.abs(v) - 0.22 + 0.15 * np.abs(u) / larg), np.maximum(1.0 - w, w - comp))
    lam = menos(lam, np.maximum(np.maximum(np.abs(u) - 0.1, np.abs(v) - 0.5), np.maximum(1.6 - w, w - comp * 0.7)), 0.03)  # sulco
    guarda = caixa_local(u, v, w, (0, 0, 0.85), (1.6 * larg, 0.32, 0.25), 0.12)
    pega = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.33, np.maximum(-cabo + 0.8 - w, w - 0.8))
    pega = pega + 0.05 * np.abs(np.sin(w * 9))
    pomo = np.sqrt(u ** 2 + v ** 2 + (w + cabo - 0.6) ** 2) - 0.5
    return np.minimum.reduce([lam, guarda, pega, pomo])


def caixa_local(u, v, w, c, meia, r=0.0):
    q = [np.abs(u - c[0]) - meia[0] + r, np.abs(v - c[1]) - meia[1] + r, np.abs(w - c[2]) - meia[2] + r]
    return np.sqrt(np.maximum(q[0], 0) ** 2 + np.maximum(q[1], 0) ** 2 + np.maximum(q[2], 0) ** 2) + np.minimum(np.maximum.reduce(q), 0) - r


def machado(g, mao_, dirv, comp=11.0, duplo=False, plano=(1, 0, 0)):
    u, v, w = _local(g, mao_, dirv, plano)
    cabo = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.38, np.maximum(-2.5 - w, w - comp))
    lam = None
    for s_ in ((-1, 1) if duplo else (1,)):
        l = np.maximum(np.sqrt((u - s_ * 0.6) ** 2 + (w - comp + 1.4) ** 2) - 2.6, -s_ * u)
        l = np.maximum(l, np.abs(v) - 0.35 + 0.1 * np.abs(u))
        lam = l if lam is None else np.minimum(lam, l)
    return np.minimum(cabo, lam)


def martelo(g, mao_, dirv, comp=10.0, plano=(1, 0, 0)):
    u, v, w = _local(g, mao_, dirv, plano)
    cabo = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.35, np.maximum(-2.0 - w, w - comp))
    cab = caixa_local(u, v, w, (0, 0, comp), (1.9, 1.0, 1.0), 0.2)
    return np.minimum(cabo, cab)


def cajado(g, mao_, dirv, acima=9.0, abaixo=None, topo="cristal", plano=(1, 0, 0)):
    u, v, w = _local(g, mao_, dirv, plano)
    abaixo = abaixo if abaixo is not None else 20.0
    hast = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.36 - 0.06 * np.sin(w * 1.3), np.maximum(-abaixo - w, w - acima))
    if topo == "cristal":
        cr = np.maximum(np.abs(u) + np.abs(v) - 0.9 * np.clip((acima + 2.6 - w) / 1.4, 0, 1), np.maximum(acima - 0.3 - w, w - acima - 2.6))
        garra = np.maximum(np.abs(np.sqrt(u ** 2 + v ** 2) - 0.9) - 0.18, np.abs(w - acima) - 0.6)
        return np.minimum.reduce([hast, cr, garra])
    if topo == "galho":
        g1 = capsula_l(u, v, w, (0, 0, acima - 1), (1.2, 0.3, acima + 1.8), 0.3, 0.12)
        g2 = capsula_l(u, v, w, (0, 0, acima - 0.5), (-1.0, -0.4, acima + 1.4), 0.28, 0.1)
        return np.minimum.reduce([hast, g1, g2, np.sqrt(u ** 2 + v ** 2 + (w - acima) ** 2) - 0.55])
    return hast


def capsula_l(u, v, w, a, b, r1, r2=None):
    r2 = r1 if r2 is None else r2
    ba = np.array(b, float) - np.array(a, float)
    L2 = float(ba @ ba)
    pu, pv, pw = u - a[0], v - a[1], w - a[2]
    h = np.clip((pu * ba[0] + pv * ba[1] + pw * ba[2]) / L2, 0, 1)
    return np.sqrt((pu - ba[0] * h) ** 2 + (pv - ba[1] * h) ** 2 + (pw - ba[2] * h) ** 2) - (r1 + (r2 - r1) * h)


def adaga(g, mao_, dirv, comp=5.0, plano=(1, 0, 0)):
    return espada(g, mao_, dirv, comp=comp, larg=0.8, plano=plano, cabo=1.8)


def escudo(g, centro, normal, r=4.6, tipo="redondo", emblema=None):
    """escudo redondo (com umbo) ou heráldico, face para `normal`."""
    u, v, w = _local(g, centro, normal, plano=(0, 0, 1))
    if tipo == "redondo":
        d2 = np.sqrt(u ** 2 + v ** 2) - r
        curva = 0.035 * (u ** 2 + v ** 2)
    else:                                                                       # heráldico (u = vertical)
        d2 = np.maximum(u - r * 0.9, np.sqrt((np.abs(v) + r * 0.25) ** 2 + np.minimum(u, 0) ** 2 * 0.85) - r)
        curva = 0.03 * v ** 2
    d = np.maximum(d2, np.abs(w + curva) - 0.35)
    borda = np.maximum(np.abs(d2 + 0.25) - 0.25, np.abs(w + curva - 0.12) - 0.42)
    d = np.minimum(d, borda)
    if tipo == "redondo":
        d = smin(d, np.sqrt(u ** 2 + v ** 2 + (w - 0.3) ** 2) - 1.1, 0.3)
    if emblema is not None:
        d = smin(d, np.maximum(emblema(u, v), np.abs(w + curva - 0.35) - 0.25), 0.05)
    return d


def arco(g, mao_, plano_n=(0, -1, 0), alt=17.0, puxado=False):
    """arco longo vertical na mão, corda e (se puxado) flecha."""
    u, v, w = _local(g, mao_, (0, 0, 1), plano=plano_n)
    curva = 0.022 * w ** 2
    a = np.maximum(np.sqrt((u + 0.0 - (-curva + 0.0)) ** 2 + v ** 2) - (0.42 - 0.012 * np.abs(w)), np.abs(w) - alt / 2)
    ponta = alt / 2
    corda_u = -0.022 * ponta ** 2 + (2.5 if puxado else 0) * np.clip(1 - np.abs(w) / ponta, 0, 1)
    corda = np.maximum(np.sqrt((u - corda_u) ** 2 + v ** 2) - 0.12, np.abs(w) - ponta)
    return np.minimum(a, corda)


def livro(g, centro, normal, larg=2.6, alt=3.4, esp=0.9, aberto=False):
    u, v, w = _local(g, centro, normal, plano=(0, 0, 1))
    if not aberto:
        d = caixa_local(u, v, w, (0, 0, 0), (alt / 2, larg / 2, esp / 2), 0.12)
        return np.minimum(d, caixa_local(u, v, w, (0, -larg / 2 - 0.05, 0), (alt / 2 + 0.05, 0.1, esp / 2 + 0.05), 0.08))
    pag = None
    for s_ in (-1, 1):
        c = caixa_local(u, v - s_ * larg * 0.5, w - 0.12 * np.abs(v) - 0.0, (0, 0, 0), (alt / 2, larg / 2, 0.22), 0.1)
        pag = c if pag is None else np.minimum(pag, c)
    return pag


def pistola(g, mao_, dirv, plano=(0, 0, 1)):
    u, v, w = _local(g, mao_, dirv, plano)
    cano = caixa_local(u, v, w, (0.75, 0, 2.0), (0.38, 0.28, 2.4), 0.1)
    pega = caixa_local(u, v, w, (-0.2, 0, 0.0), (0.75, 0.26, 0.4), 0.15)
    return np.minimum(cano, pega)


def espingarda(g, mao_, dirv, comp=12.0, plano=(0, 0, 1)):
    """escopeta segura com a mão de trás em mao_ (coronha atrás, cano à frente)."""
    u, v, w = _local(g, mao_, dirv, plano)
    cano = np.maximum(np.sqrt((u - 0.7) ** 2 + v ** 2) - 0.55, np.maximum(0.5 - w, w - comp))
    tubo_ = np.maximum(np.sqrt((u + 0.15) ** 2 + v ** 2) - 0.5, np.maximum(2.5 - w, w - comp * 0.75))
    corpo_ = caixa_local(u, v, w, (0.25, 0, 1.2), (0.95, 0.55, 1.9), 0.2)
    coronha = caixa_local(u, v, w, (-0.7, 0, -2.8), (1.15, 0.55, 2.6), 0.35)
    bomba = np.maximum(np.sqrt((u + 0.15) ** 2 + v ** 2) - 0.8, np.abs(w - comp * 0.55) - 1.5)
    bomba = bomba + 0.08 * (np.abs(np.mod(w, 0.5) - 0.25) < 0.08)
    return np.minimum.reduce([cano, tubo_, corpo_, coronha, bomba])


def faca(g, mao_, dirv, comp=4.5, plano=(1, 0, 0)):
    """facão: lâmina larga de um fio."""
    u, v, w = _local(g, mao_, dirv, plano)
    lam = np.maximum(np.maximum(u - 0.55, -u - 0.55 + 0.6 * np.clip((w - comp + 1.5) / 1.5, 0, 1)), np.maximum(np.abs(v) - 0.18 + 0.1 * (u + 0.55), np.maximum(0.6 - w, w - comp)))
    pega = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.33, np.maximum(-1.6 - w, w - 0.6))
    return np.minimum(lam, pega)


def lanterna(g, mao_, dirv, plano=(0, 0, 1)):
    u, v, w = _local(g, mao_, dirv, plano)
    corpo_ = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.45, np.maximum(-1.0 - w, w - 2.2))
    cab = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.75 * np.clip((w - 1.6) / 1.2 + 0.6, 0.6, 1), np.maximum(1.6 - w, w - 3.2))
    return np.minimum(corpo_, cab)


def camera(g, centro, normal, plano=(0, 0, 1)):
    u, v, w = _local(g, centro, normal, plano)
    c = caixa_local(u, v, w, (0, 0, 0), (1.1, 1.6, 0.7), 0.25)
    lente = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.7, np.maximum(-w, w - 1.5))
    return np.minimum(c, lente)


def vela(g, base_, alt=2.0, r=0.4):
    x, y, z = base_
    v = np.maximum(np.sqrt((g.x - x) ** 2 + (g.y - y) ** 2) - r, np.maximum(z - g.z, g.z - z - alt))
    ch = smin(elipsoide(g, (x, y, z + alt + 0.55), (0.28, 0.28, 0.45)), capsula(g, (x, y, z + alt + 0.6), (x, y, z + alt + 1.3), 0.18, 0.04), 0.15)
    return np.minimum(v, ch)


# ------------------------------------------------------------------ base
def base(g, r=12.5, tipo="pedra", semente=1):
    """base redonda de 25 mm com chão temático: pedra (lajes), terra, grama, asfalto, madeira, neve."""
    rad = np.sqrt(g.x ** 2 + g.y ** 2)
    d = np.maximum(rad - r, np.maximum(-g.z, g.z - BASE))
    d = smax(d, g.z - BASE, 0.6)
    topo = np.clip(1 - np.abs(g.z - BASE) / 0.8, 0, 1) * (rad < r - 0.6)
    if tipo == "pedra":
        tex = tijolos(g.x, g.y, larg=6.5, alt=5.0, junta=0.35, prof=0.45, semente=semente, irregular=0.3)
    elif tipo == "terra":
        tex = -0.35 * np.clip(fbm(g, 1.6, semente, 3), 0, None) + 0.05 * ruido_cel(g, 0.3, semente)
    elif tipo == "asfalto":
        rach = np.abs(ruido_cel(g, 7.0, semente)) - 0.05
        tex = 0.03 * ruido_cel(g, 0.25, semente) + 0.35 * np.clip(-rach / 0.06, 0, 1)
    elif tipo == "madeira":
        tex = madeira(g.x, g.y, tabua=4.2, fenda=0.25, prof=0.3, veio=0.06, semente=semente)
    else:
        tex = -0.25 * np.clip(fbm(g, 2.5, semente, 2), 0, None)
    return d + topo * tex


def grama(g, pontos, alt=1.6):
    d = None
    for (x, y) in pontos:
        for j in range(5):
            a = j * 1.26
            e = capsula(g, (x, y, BASE), (x + 0.6 * np.cos(a), y + 0.6 * np.sin(a), BASE + alt * (0.7 + 0.3 * (j % 2))), 0.22, 0.05)
            d = e if d is None else np.minimum(d, e)
    return d


def montar(partes_cor, regioes_ordem=("c4", "c3", "c2")):
    """une as partes {cor: campo} e devolve (tudo, regioes) para esculpir; c1 é o resto."""
    tudo = np.minimum.reduce([v for v in partes_cor.values() if v is not None])
    reg = {k: partes_cor[k] for k in regioes_ordem if partes_cor.get(k) is not None}
    return tudo, reg


# ------------------------------------------------------------------ execução
MN_MINI, MX_MINI = (-13.5, -13.5, 0), (13.5, 13.5, 38)


def rodar_mini(arquivo, classe, campo_de, mn=MN_MINI, mx=MX_MINI, passo_padrao=0.07):
    """campo_de(sexo) -> função campo(g). Gera <classe>_m e <classe>_f (ou só um: --m / --f) em stl/."""
    passo, _ = args(passo_padrao)
    sexos = [s for s in ("m", "f") if f"--{s}" in sys.argv] or ["m", "f"]
    for sx in sexos:
        r = esculpir(campo_de(sx), mn, mx, passo, saida(arquivo, f"{classe}_{sx}", False), suaviza=2, min_area=0.3)
        print(classe, sx, {k: v[1] for k, v in r.items()}, flush=True)
