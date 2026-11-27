"""Biblioteca de figura humana para miniaturas de mesa (escala heroica 28–32 mm, base de 25 mm).

Unidades em mm. A figura fica de pé com os pés em z = BASE, de frente para −y; o lado "d" fica em +x.

Ideias principais
- Esqueleto com juntas resolvidas por IK: a pose diz onde ficam mãos e pés (e para onde dobram cotovelos e
  joelhos); os comprimentos de braço e perna nunca esticam.
- O corpo é feito de massas anatômicas (elipsoides orientados ao longo dos ossos), não de tubos iguais.
- Cada parte do corpo aceita uma "folga" e: a roupa é a mesma parte inflada e recortada; o degrau entre roupa e
  corpo (barras, punhos, golas, cano de bota) é o que faz a roupa ser lida na mesa.

Fluxo:
    J = esqueleto("f", mao_d=(...), mao_e=(...), cotovelo_d=polo, ...)
    P = partes(g, J)                 # corpo nu, por parte
    roupa = veste(g, J, ...)         # roupas
    cab, cabelo = cabeca(g, J, ...)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *  # noqa: F401,F403

BASE = 3.0                       # altura da base redonda


def _v(a):
    return np.array(a, float)


vec = _v


def _n(a):
    a = _v(a)
    return a / np.linalg.norm(a)


# ------------------------------------------------------------------ geometria local
def _frame(dirv, plano=None):
    z_ = _n(dirv)
    a = _v(plano) if plano is not None else (np.array([0, 0, 1.0]) if abs(z_[2]) < 0.9 else np.array([1.0, 0, 0]))
    x_ = a - z_ * (a @ z_)
    if np.linalg.norm(x_) < 1e-6:
        x_ = np.cross([0, 1.0, 0], z_)
    x_ = x_ / np.linalg.norm(x_)
    return x_, np.cross(z_, x_), z_


def local(g, origem, dirv, plano=None):
    """coordenadas (u, v, w) de g num referencial com w ao longo de dirv e u na direção de `plano`."""
    x_, y_, z_ = _frame(dirv, plano)
    X, Y, Z = g.x - origem[0], g.y - origem[1], g.z - origem[2]
    return (X * x_[0] + Y * x_[1] + Z * x_[2], X * y_[0] + Y * y_[1] + Z * y_[2], X * z_[0] + Y * z_[1] + Z * z_[2])


def elip_l(u, v, w, a, b, c):
    """elipsoide (semi-eixos a, b, c) em coordenadas locais; distância aproximada."""
    k = np.sqrt((u / a) ** 2 + (v / b) ** 2 + (w / c) ** 2)
    return (k - 1) * min(a, b, c)


def caixa_l(u, v, w, c, meia, r=0.0):
    q = [np.abs(u - c[0]) - meia[0] + r, np.abs(v - c[1]) - meia[1] + r, np.abs(w - c[2]) - meia[2] + r]
    return np.sqrt(np.maximum(q[0], 0) ** 2 + np.maximum(q[1], 0) ** 2 + np.maximum(q[2], 0) ** 2) + np.minimum(np.maximum.reduce(q), 0) - r


def capsula_l(u, v, w, a, b, r1, r2=None):
    r2 = r1 if r2 is None else r2
    ba = _v(b) - _v(a)
    L2 = float(ba @ ba)
    pu, pv, pw = u - a[0], v - a[1], w - a[2]
    h = np.clip((pu * ba[0] + pv * ba[1] + pw * ba[2]) / L2, 0, 1)
    return np.sqrt((pu - ba[0] * h) ** 2 + (pv - ba[1] * h) ** 2 + (pw - ba[2] * h) ** 2) - (r1 + (r2 - r1) * h)


def massa(g, a, b, t, raios, desl=(0, 0, 0), plano=None):
    """músculo: elipsoide com o eixo longo (raios[2]) ao longo do osso a→b, centrado na fração t (+ desl no mundo)."""
    c = _v(a) + (_v(b) - _v(a)) * t + _v(desl)
    u, v, w = local(g, c, _v(b) - _v(a), plano)
    return elip_l(u, v, w, *raios)


def trecho(g, a, b, t0, t1):
    """campo < 0 entre as frações t0 e t1 do segmento a→b (fatia perpendicular ao osso)."""
    ba = _v(b) - _v(a)
    L = float(np.linalg.norm(ba))
    h = ((g.x - a[0]) * ba[0] + (g.y - a[1]) * ba[1] + (g.z - a[2]) * ba[2]) / (L * L)
    return np.maximum(t0 - h, h - t1) * L


def ik(a, c, L1, L2, polo):
    """junta do meio entre a e c (comprimentos L1, L2), dobrando para o lado de `polo` (direção)."""
    a, c = _v(a), _v(c)
    d = c - a
    D = min(float(np.linalg.norm(d)), L1 + L2 - 1e-3)
    u = d / np.linalg.norm(d)
    c = a + u * D
    x = (L1 ** 2 - L2 ** 2 + D ** 2) / (2 * D)
    h = np.sqrt(max(L1 ** 2 - x ** 2, 0.0))
    p = _v(polo) - u * (_v(polo) @ u)
    p = p / (np.linalg.norm(p) + 1e-9)
    return tuple(a + u * x + p * h), tuple(c)


# ------------------------------------------------------------------ esqueleto
def esqueleto(sexo="m", escala=1.0, giro=0.0, inclina=0.0, cabeca_giro=0.0, cabeca_inclina=0.0, peso_d=0.5, **pose):
    """juntas da figura. pose: mao_e/mao_d, pe_e/pe_d (pontos absolutos) e polos cotovelo_e/d, joelho_e/d
    (direções para onde a junta dobra). giro: tronco girado (graus, em z); inclina: tronco para a frente (graus).
    peso_d: 0..1, quanto o quadril desce/escorrega para o lado da perna de apoio (contrapposto)."""
    f = sexo == "f"
    s = escala * (0.95 if f else 1.0)
    Z = lambda v: BASE + v * s
    J = {"sexo": sexo, "s": s, "giro": giro, "inclina": inclina, "cabeca_giro": cabeca_giro, "cabeca_inclina": cabeca_inclina}
    # quadril com contrapposto: desloca para o lado de apoio e inclina
    dx = (peso_d - 0.5) * 0.9 * s
    pel = _v((dx, 0.3 * s, Z(16.4)))
    qd = (2.05 if f else 1.95) * s
    inc_q = (peso_d - 0.5) * 0.6 * s
    J["pelve"] = tuple(pel)
    J["quadril_e"] = tuple(pel + _v((-qd, -0.1 * s, -0.55 * s + inc_q)))
    J["quadril_d"] = tuple(pel + _v((qd, -0.1 * s, -0.55 * s - inc_q)))
    # tronco: gira em torno da pelve e inclina para a frente
    R = np.array(mul(rot_z(giro), rot_x(-inclina)))

    def T(p):
        return tuple(pel + R @ (_v(p) - pel))

    om = (3.35 if f else 3.95) * s
    J["cintura"] = T((dx, 0.15 * s, Z(19.6)))
    J["peito"] = T((dx * 0.6, 0.0, Z(23.1)))
    J["pescoco"] = T((dx * 0.4, 0.15 * s, Z(27.0)))
    J["ombro_e"] = T((dx * 0.5 - om, 0.35 * s, Z(26.0 - (peso_d - 0.5) * 0.4)))
    J["ombro_d"] = T((dx * 0.5 + om, 0.35 * s, Z(26.0 + (peso_d - 0.5) * 0.4)))
    J["cabeca"] = T((dx * 0.4, -0.25 * s, Z(30.0)))
    J["R_tronco"] = R
    # braços (IK)
    Lb, La = 5.3 * s, 4.8 * s
    for lado, sx in (("e", -1), ("d", 1)):
        o = _v(J["ombro_" + lado])
        alvo = pose.get("mao_" + lado, tuple(o + _v((sx * 1.4 * s, -0.2 * s, -9.6 * s))))
        polo = pose.get("cotovelo_" + lado, (sx * 0.3, 1.0, -0.2))
        J["cotovelo_" + lado], J["mao_" + lado] = ik(o, alvo, Lb, La, polo)
    # pernas (IK)
    Lc, Lt = 7.3 * s, 7.3 * s
    for lado, sx in (("e", -1), ("d", 1)):
        q = _v(J["quadril_" + lado])
        alvo = pose.get("pe_" + lado, (q[0] + sx * 0.35 * s, q[1] - 0.2 * s, BASE + 1.05 * s))
        polo = pose.get("joelho_" + lado, (sx * 0.15, -1.0, 0.0))
        J["joelho_" + lado], J["pe_" + lado] = ik(q, alvo, Lc, Lt, polo)
    return J


# ------------------------------------------------------------------ corpo por partes
def _tronco_l(g, J):
    """g visto no referencial do tronco (gira e inclina junto)."""
    R = J["R_tronco"]
    return Vista(g, J["pelve"], R)


_CACHE = {"g": None, "d": {}}


class _Partes:
    """partes do corpo calculadas sob demanda (e guardadas enquanto a mesma grade estiver em uso)."""
    def __init__(self, g, J, e, m, k):
        self.g, self.J, self.chave = g, J, (id(J), round(float(e), 4), m, k)
        self.e, self.m, self.k = e, m, k
        if _CACHE["g"] is not g:
            _CACHE["g"], _CACHE["d"] = g, {}

    def __getitem__(self, nome):
        ch = self.chave + (nome,)
        d = _CACHE["d"]
        if ch not in d:
            d[ch] = _parte(self.g, self.J, nome, self.e, self.m, self.k)
        return d[ch]


def partes(g, J, e=0.0, musculo=1.0, peso=1.0):
    """partes do corpo (tronco, gluteo, pescoco, braco_x, antebraco_x, mao_x, coxa_x, canela_x, pe_x),
    todas infladas de `e` (folga de roupa); calculadas só quando usadas."""
    return _Partes(g, J, e, musculo, peso)


def _parte(g, J, nome, e, m, k):
    f, s = J["sexo"] == "f", J["s"]
    p0 = _v(J["pelve"])
    zc = lambda v: BASE + v * s
    dx = p0[0]
    if nome == "tronco":
        gt = _tronco_l(g, J)
        if f:
            torax = elipsoide(gt, (dx, 0.05 * s, zc(23.0)), (3.05 * s * m + e, 2.15 * s * k + e, 3.3 * s + e))
            abd = elipsoide(gt, (dx, -0.05 * s, zc(19.6)), (2.25 * s * k + e, 1.7 * s * k + e, 2.5 * s + e))
            pelv = elipsoide(g, (dx, 0.3 * s, zc(16.6)), (3.15 * s * k + e, 2.3 * s * k + e, 2.5 * s + e))
        else:
            torax = elipsoide(gt, (dx, 0.1 * s, zc(23.1)), (3.55 * s * m + e, 2.45 * s * k + e, 3.5 * s + e))
            abd = elipsoide(gt, (dx, -0.05 * s, zc(19.6)), (2.75 * s * k + e, 1.95 * s * k + e, 2.6 * s + e))
            pelv = elipsoide(g, (dx, 0.3 * s, zc(16.6)), (3.05 * s * k + e, 2.2 * s * k + e, 2.3 * s + e))
        t = smin(smin(torax, abd, 1.6 * s), pelv, 1.4 * s)
        for sx in (-1, 1):
            if f:
                t = smin(t, esfera(gt, (dx + sx * 1.3 * s, -1.75 * s, zc(23.2)), 1.3 * s + e), 0.7 * s)
            else:
                t = smin(t, elipsoide(gt, (dx + sx * 1.6 * s, -1.65 * s, zc(24.0)), (1.75 * s * m + e, 0.95 * s + e, 1.35 * s + e)), 0.7 * s)
            t = smin(t, elipsoide(gt, (dx + sx * 1.5 * s, 1.65 * s, zc(24.4)), (1.5 * s + e, 0.9 * s + e, 1.7 * s + e)), 0.8 * s)     # omoplatas
        om = (3.35 if f else 3.95) * s
        t = smin(t, capsula(gt, (dx - om * 0.75, 0.35 * s, zc(25.8)), (dx + om * 0.75, 0.35 * s, zc(25.8)), (1.05 if f else 1.3) * s * m + e), 1.3 * s)
        return smin(t, capsula(gt, (dx - 1.4 * s, 0.6 * s, zc(26.3)), (dx + 1.4 * s, 0.6 * s, zc(26.3)), (0.9 if f else 1.25) * s + e), 1.1 * s)
    if nome == "gluteo":
        r = (1.6 if f else 1.55) * s + e
        return np.minimum(esfera(g, (dx - 1.3 * s, 1.5 * s, zc(15.9)), r), esfera(g, (dx + 1.3 * s, 1.5 * s, zc(15.9)), r))
    if nome == "pescoco":
        pe = J["pescoco"]
        return capsula(g, pe, (pe[0], pe[1] - 0.15 * s, pe[2] + 1.7 * s), (1.0 if f else 1.2) * s + e)
    parte, lado = nome.rsplit("_", 1)
    sx = -1 if lado == "e" else 1
    if parte in ("braco", "antebraco", "mao"):
        o, co, w = J["ombro_" + lado], J["cotovelo_" + lado], J["mao_" + lado]
        if parte == "braco":
            delt = massa(g, o, co, 0.2, ((1.05 if f else 1.3) * s * m + e, (1.15 if f else 1.4) * s * m + e, 1.8 * s + e), desl=(sx * 0.1 * s, 0, 0))
            braco = capsula(g, o, co, (1.0 if f else 1.15) * s * m + e, (0.75 if f else 0.85) * s + e)
            bic = massa(g, o, co, 0.55, ((0.85 if f else 1.05) * s * m + e, (0.9 if f else 1.1) * s * m + e, 1.8 * s + e))
            return smin(smin(delt, braco, 0.6 * s), bic, 0.5 * s)
        if parte == "antebraco":
            ante = capsula(g, co, w, (0.82 if f else 0.95) * s + e, (0.55 if f else 0.62) * s + e)
            return smin(ante, massa(g, co, w, 0.28, ((0.85 if f else 1.02) * s * m + e, (0.8 if f else 0.95) * s * m + e, 1.55 * s + e)), 0.5 * s)
        if J.get("aberta_" + lado):
            return mao_aberta(g, co, w, s, e, J["aberta_" + lado])
        return mao(g, co, w, s, e)
    q, j, a = J["quadril_" + lado], J["joelho_" + lado], J["pe_" + lado]
    if parte == "coxa":
        coxa = capsula(g, q, j, (2.15 if f else 2.05) * s * k + e, 1.2 * s + e)
        quad = massa(g, q, j, 0.42, ((1.75 if f else 1.7) * s * k + e, 1.7 * s * k + e, 3.1 * s + e), desl=(sx * 0.15 * s, -0.25 * s, 0))
        return smin(smin(coxa, quad, 0.8 * s), esfera(g, j, 1.15 * s + e), 0.6 * s)
    if parte == "canela":
        can = capsula(g, j, a, 1.15 * s + e, 0.72 * s + e)
        return smin(can, massa(g, j, a, 0.3, (1.15 * s * k + e, 1.25 * s * k + e, 2.2 * s + e), desl=(0, 0.45 * s, 0)), 0.6 * s)
    return pe_(g, a, s, e)


def corpo(g, J, **kw):
    P = partes(g, J, **kw)
    s = J["s"]
    b = smin(P["tronco"], P["gluteo"], 0.8 * s)
    b = smin(b, P["pescoco"], 0.8 * s)
    for lado in ("e", "d"):
        b = smin(b, P["braco_" + lado], 0.9 * s)
        b = smin(b, P["antebraco_" + lado], 0.5 * s)
        b = smin(b, P["mao_" + lado], 0.25 * s)
        b = smin(b, P["coxa_" + lado], 1.0 * s)
        b = smin(b, P["canela_" + lado], 0.6 * s)
        b = smin(b, P["pe_" + lado], 0.35 * s)
    return b


def mao_aberta(g, cotovelo, w, s, e=0.0, palma=(0, -1, 0)):
    """mão aberta com dedos abertos em leque; palma virada para `palma`."""
    d = _n(_v(w) - _v(cotovelo))
    c = _v(w) + d * 0.6 * s
    u, v, ww = local(g, c, d, plano=palma)                 # u = para onde a palma olha
    pal = elip_l(u, v, ww, 0.42 * s + e, 0.8 * s + e, 0.75 * s + e)
    dedos = None
    for k, (ang, L) in enumerate([(-0.45, 1.35), (-0.15, 1.5), (0.15, 1.45), (0.45, 1.2)]):
        b = (0, 0.55 * s * np.sin(ang) * 1.6, 0.6 * s)
        t = (-0.25 * s, b[1] + L * s * np.sin(ang), b[2] + L * s * np.cos(ang))
        f_ = capsula_l(u, v, ww, b, t, 0.24 * s + e, 0.17 * s + e)
        dedos = f_ if dedos is None else np.minimum(dedos, f_)
    pol = capsula_l(u, v, ww, (0, -0.55 * s, -0.2 * s), (-0.35 * s, -1.3 * s, 0.45 * s), 0.27 * s + e, 0.2 * s + e)
    return smin(smin(pal, dedos, 0.2 * s), pol, 0.2 * s)


def mao(g, cotovelo, w, s, e=0.0):
    """mão fechada: punho em volta de um cabo que passa por `w` perpendicular ao antebraço."""
    d = _n(_v(w) - _v(cotovelo))
    c = _v(w) + d * 0.65 * s
    u, v, ww = local(g, c, d)
    palma = elip_l(u, v, ww, 0.88 * s + e, 0.72 * s + e, 0.95 * s + e)
    nos = capsula_l(u, v, ww, (-0.55 * s, -0.55 * s, 0.35 * s), (0.55 * s, -0.55 * s, 0.35 * s), 0.38 * s + e)
    pol = capsula_l(u, v, ww, (0.0, 0.6 * s, -0.2 * s), (0.2 * s, 0.5 * s, 0.75 * s), 0.3 * s + e)
    return smin(smin(palma, nos, 0.3 * s), pol, 0.2 * s)


def pe_(g, a, s, e=0.0):
    x, y, z = a
    pe = smin(elipsoide(g, (x, y - 1.05 * s, BASE + 0.5 * s), (0.85 * s + e, 1.8 * s + e, 0.55 * s + e)),
              esfera(g, (x, y + 0.25 * s, BASE + 0.75 * s), 0.78 * s + e), 0.45 * s)
    return np.maximum(pe, BASE - g.z)


# ------------------------------------------------------------------ cabeça
def cabeca(g, J, cabelo="curto", barba=None, expressao="seria", escala=1.12):
    """cabeça heroica (um pouco grande) com rosto e cabelo. Devolve (cabeça, cabelo|None).
    cabelo: careca, raspado, curto, topete, longo, rabo, coque, trancas, moicano, chanel."""
    f = J["sexo"] == "f"
    s = J["s"] * escala
    c = _v(J["cabeca"])
    R = np.array(mul(rot_z(J.get("giro", 0) + J.get("cabeca_giro", 0)), rot_x(-J.get("cabeca_inclina", 0))))
    gh = Vista(g, tuple(c), R)
    X, Y, Z = gh.x - c[0], gh.y - c[1], gh.z - c[2]          # coordenadas da cabeça (frente = −Y)
    cr = elip_l(X, Y - 0.2 * s, Z - 0.35 * s, 1.95 * s, 2.2 * s, 2.15 * s)
    face = elip_l(X, Y + 0.7 * s, Z + 0.55 * s, (1.5 if f else 1.65) * s, 1.55 * s, 1.85 * s)
    h = smin(cr, face, 0.9 * s)
    # mandíbula e queixo
    jaw_w = (1.05 if f else 1.3) * s
    for sx in (-1, 1):
        h = smin(h, elip_l(X - sx * jaw_w, Y + 0.55 * s, Z + 1.35 * s, 0.55 * s, 0.9 * s, 0.75 * s), 0.6 * s)
    h = smin(h, elip_l(X, Y + 1.5 * s, Z + 1.95 * s, (0.55 if f else 0.75) * s, 0.55 * s, (0.5 if f else 0.6) * s), 0.6 * s)
    # testa e sobrancelhas
    h = smin(h, capsula_l(X, Y, Z, (-1.0 * s, -1.75 * s, 0.5 * s), (1.0 * s, -1.75 * s, 0.5 * s), (0.25 if f else 0.33) * s), 0.35 * s)
    for sx in (-1, 1):
        # órbita funda, globo, pálpebra superior
        h = menos(h, elip_l(X - sx * 0.72 * s, Y + 2.0 * s, Z - 0.05 * s, 0.48 * s, 0.4 * s, 0.36 * s), 0.18 * s)
        h = np.minimum(h, elip_l(X - sx * 0.72 * s, Y + 1.72 * s, Z - 0.03 * s, 0.33 * s, 0.26 * s, 0.24 * s))
        h = smin(h, capsula_l(X, Y, Z, (sx * 0.45 * s, -1.92 * s, 0.17 * s), (sx * 1.05 * s, -1.82 * s, 0.14 * s), 0.08 * s), 0.08 * s)
        # maçã do rosto
        h = smin(h, elip_l(X - sx * 1.05 * s, Y + 1.45 * s, Z + 0.55 * s, 0.5 * s, 0.4 * s, 0.4 * s), 0.4 * s)
        # orelha
        h = smin(h, elip_l(X - sx * 1.95 * s, Y - 0.15 * s, Z + 0.1 * s, 0.22 * s, 0.45 * s, 0.68 * s), 0.2 * s)
    # nariz (cunha) e narinas
    nariz = capsula_l(X, Y, Z, (0, -2.0 * s, 0.1 * s), (0, -2.42 * s, -0.75 * s), 0.18 * s, (0.26 if f else 0.32) * s)
    nariz = smin(nariz, elip_l(X, Y + 2.25 * s, Z + 0.8 * s, (0.38 if f else 0.45) * s, 0.25 * s, 0.2 * s), 0.12 * s)
    h = smin(h, nariz, 0.2 * s)
    # boca: lábios e fenda
    bz = -1.32 * s
    h = smin(h, elip_l(X, Y + 1.98 * s, Z - bz - 0.1 * s, 0.5 * s, 0.18 * s, (0.13 if f else 0.1) * s), 0.12 * s)
    h = smin(h, elip_l(X, Y + 1.93 * s, Z - bz + 0.18 * s, 0.45 * s, 0.17 * s, (0.15 if f else 0.11) * s), 0.12 * s)
    zb = bz + (0.03 * s - 0.18 * s * (X / (0.5 * s)) ** 2 if expressao == "sorriso" else 0)
    if expressao == "grito":
        h = menos(h, elip_l(X, Y + 2.0 * s, Z - bz + 0.1 * s, 0.38 * s, 0.4 * s, 0.32 * s), 0.08 * s)
    else:
        h = menos(h, np.maximum(np.abs(Z - zb) - 0.04 * s, np.maximum(np.abs(X) - 0.46 * s, -(Y + 2.3 * s))), 0.04 * s)
    if expressao == "bravo":
        for sx in (-1, 1):
            h = smin(h, capsula_l(X, Y, Z, (sx * 0.25 * s, -2.0 * s, 0.3 * s), (sx * 1.0 * s, -1.85 * s, 0.55 * s), 0.14 * s), 0.1 * s)
    ca = _cabelo(X, Y, Z, s, cabelo, f, cr)
    if barba:
        if barba == "cheia":
            bb = elip_l(X, Y + 1.0 * s, Z + 1.45 * s, 1.75 * s, 1.35 * s, 1.35 * s)
            bb = np.maximum(bb, np.maximum(-(Y + 2.55 * s), Z + 0.2 * s - 0.0))
            bb = smin(bb, elip_l(X, Y + 1.6 * s, Z + 2.5 * s, 0.9 * s, 0.7 * s, 0.9 * s), 0.4 * s)
            bigode = capsula_l(X, Y, Z, (-0.7 * s, -2.2 * s, bz + 0.2 * s), (0.7 * s, -2.2 * s, bz + 0.2 * s), 0.18 * s)
            bb = smin(np.maximum(bb, -elip_l(X, Y + 2.0 * s, Z - bz, 0.5 * s, 0.6 * s, 0.22 * s)), bigode, 0.15 * s)
        else:
            bb = smin(elip_l(X, Y + 1.7 * s, Z + 2.05 * s, 0.6 * s, 0.55 * s, 0.7 * s),
                      capsula_l(X, Y, Z, (-0.55 * s, -2.12 * s, bz + 0.22 * s), (0.55 * s, -2.12 * s, bz + 0.22 * s), 0.13 * s), 0.2 * s)
        bb = bb + 0.07 * s * np.abs(np.sin(X * 8 / s + Z * 2 / s))
        ca = bb if ca is None else np.minimum(ca, bb)
    h = h + 0.008 * ruido_cel(gh, 0.25, 7)
    return h, ca


def _cabelo(X, Y, Z, s, tipo, f, cr):
    """cabelo como casca sobre o crânio, com linha do cabelo, franja e mechas."""
    if tipo == "careca":
        return None
    casca = elip_l(X, Y - 0.25 * s, Z - 0.45 * s, 2.18 * s, 2.45 * s, 2.38 * s)
    acima = 0.7 * s - 0.35 * s * np.cos(X * 1.3 / s) - Z                     # < 0 acima da linha do cabelo
    atras = np.maximum(-Y + 0.2 * s, -1.3 * s - Z)                            # < 0 atrás e acima da nuca
    base = np.maximum(casca, np.minimum(acima, atras))
    if tipo == "raspado":
        return np.maximum(elip_l(X, Y - 0.22 * s, Z - 0.4 * s, 2.05 * s, 2.32 * s, 2.25 * s), np.minimum(acima + 0.2 * s, atras + 0.3 * s))
    ang = np.arctan2(X, -Y)
    mechas = 0.12 * s * np.abs(np.sin(ang * 13 + Z * 1.2 / s)) + 0.05 * s * np.abs(np.sin(ang * 31))
    if tipo in ("curto", "topete", "moicano", "chanel"):
        d = base + mechas
        if tipo == "topete":
            d = smin(d, elip_l(X, Y + 1.0 * s, Z - 2.15 * s, 1.5 * s, 1.3 * s, 0.85 * s) + mechas, 0.5 * s)
        if tipo == "moicano":
            lados = np.maximum(elip_l(X, Y - 0.22 * s, Z - 0.4 * s, 2.03 * s, 2.3 * s, 2.23 * s), np.minimum(acima, atras))
            crista = np.maximum(elip_l(X, Y - 0.3 * s, Z - 1.5 * s, 0.55 * s, 2.55 * s, 1.9 * s) + mechas * 0.5, -(Z - 0.4 * s))
            d = np.minimum(lados, crista)
        if tipo == "chanel":
            cai = np.maximum(elip_l(X, Y - 0.15 * s, Z + 0.5 * s, 2.35 * s, 2.55 * s, 2.5 * s) + mechas, np.maximum(-(Y + 1.2 * s), -1.35 * s - Z))
            d = smin(d, cai, 0.3 * s)
        return d
    # cabelos longos
    comp = {"longo": 5.0, "rabo": 0.0, "coque": 0.0, "trancas": 0.0}.get(tipo, 3.0)
    d = base + mechas
    if comp:
        cai = capsula_l(X, Y, Z, (0, 0.9 * s, -0.2 * s), (0, 1.35 * s, -comp * s), 2.0 * s, 1.5 * s)
        cai = np.maximum(cai, -(Y - 0.15 * s)) + mechas
        d = smin(d, cai, 0.7 * s)
        for sx in (-1, 1):
            d = smin(d, capsula_l(X, Y, Z, (sx * 1.85 * s, -0.5 * s, -0.4 * s), (sx * 2.0 * s, -0.3 * s, -comp * 0.8 * s), 0.55 * s, 0.35 * s) + mechas, 0.4 * s)
    if tipo == "rabo":
        d = smin(d, tubo_l(X, Y, Z, [(0, 2.25 * s, 0.7 * s), (0, 3.0 * s, -0.5 * s), (0, 2.8 * s, -2.6 * s), (0, 2.3 * s, -4.4 * s)],
                           [0.7 * s, 0.75 * s, 0.55 * s, 0.2 * s]) + mechas, 0.35 * s)
    if tipo == "coque":
        d = smin(d, elip_l(X, Y - 1.85 * s, Z - 1.5 * s, 1.05 * s, 1.0 * s, 0.95 * s) + mechas, 0.4 * s)
    if tipo == "trancas":
        for sx in (-1, 1):
            t = tubo_l(X, Y, Z, [(sx * 1.6 * s, 0.7 * s, -0.5 * s), (sx * 1.9 * s, 0.3 * s, -2.4 * s), (sx * 1.8 * s, -0.4 * s, -4.4 * s)], [0.55 * s, 0.5 * s, 0.38 * s])
            t = t + 0.13 * s * np.abs(np.sin(Z * 4.5 / s + X))
            d = smin(d, t, 0.3 * s)
    return d


def tubo_l(u, v, w, pts, raios):
    d = None
    for i in range(len(pts) - 1):
        c = capsula_l(u, v, w, pts[i], pts[i + 1], raios[i], raios[i + 1])
        d = c if d is None else np.minimum(d, c)
    return d


# ------------------------------------------------------------------ roupas
def ondas(g, n=3.0, prof=0.1, eixo=None):
    """vincos horizontais de pano (anéis); eixo = direção do osso para vincos ao longo de mangas/pernas."""
    return prof * np.abs(np.sin(g.z * n))


def manga(g, J, lado, e=0.32, ate=1.0, punho=0.25, folga_cot=0.1):
    """manga do ombro até a fração `ate` do antebraço (0 = curta no meio do braço, 1 = no pulso), com punho."""
    s = J["s"]
    P = partes(g, J, e=e * s)
    o, co, w = J["ombro_" + lado], J["cotovelo_" + lado], J["mao_" + lado]
    br = P["braco_" + lado]
    if ate <= 0:
        return np.maximum(br, trecho(g, o, co, -0.3, 0.6))
    an = np.maximum(P["antebraco_" + lado], trecho(g, co, w, -0.2, ate))
    m = smin(br, an, 0.6 * s)
    # vincos no cotovelo (do lado de dentro) e enrugado no punho
    r_c = np.sqrt((g.x - co[0]) ** 2 + (g.y - co[1]) ** 2 + (g.z - co[2]) ** 2)
    m = m + 0.13 * s * np.clip(1 - r_c / (2.0 * s), 0, 1) * np.abs(np.sin(r_c * 4.2 / s))
    if punho:
        anel = np.maximum(partes(g, J, e=(e + punho) * s)["antebraco_" + lado], trecho(g, co, w, ate - 0.12, ate))
        m = np.minimum(m, anel)
    return m


def tronco_veste(g, J, e=0.35, z_barra=None, barra=0.0, decote=None, aberto=0.0, gola=None):
    """tronco de camisa/jaqueta/túnica: o tronco inflado, recortado na barra (z_barra, com aba que abre `barra`)."""
    s = J["s"]
    P = partes(g, J, e=e * s)
    t = smin(P["tronco"], P["gluteo"], 0.8 * s)
    zb = z_barra if z_barra is not None else J["pelve"][2] - 0.6 * s
    if barra:
        aba = np.maximum(partes(g, J, e=(e + barra) * s)["tronco"], np.maximum(zb - g.z, g.z - zb - 2.0 * s))
        t = smin(t, aba, 0.5 * s)
    t = np.maximum(t, zb - g.z)
    pe = J["pescoco"]
    t = menos(t, capsula(g, (pe[0], pe[1] - 0.1 * s, pe[2] - 0.6 * s), (pe[0], pe[1] - 0.1 * s, pe[2] + 3 * s), 1.1 * s), 0.2 * s)   # gola redonda
    if decote:
        t = menos(t, np.maximum(np.abs(g.x - pe[0]) - decote * s * np.clip((g.z - (pe[2] - 3.2 * s)) / (3.2 * s), 0, 1), (g.y - pe[1] + 0.9 * s)), 0.2 * s)
    if aberto:
        c = J["peito"]
        t = menos(t, np.maximum(np.abs(g.x - c[0]) - aberto * s * (0.3 + 0.7 * np.clip((pe[2] - g.z) / (9 * s), 0, 1)), (g.y - c[1] + 1.0 * s)), 0.1 * s)
    if gola == "alta":
        t = smin(t, np.maximum(np.abs(np.sqrt((g.x - pe[0]) ** 2 + ((g.y - pe[1]) * 1.05) ** 2) - 1.55 * s) - 0.3 * s, np.maximum(pe[2] - 0.6 * s - g.z, g.z - pe[2] - 1.0 * s)), 0.2 * s)
    elif gola == "lapela":
        for sx in (-1, 1):
            t = smin(t, np.maximum(capsula(g, (pe[0] + sx * 1.0 * s, pe[1] - 1.1 * s, pe[2] - 0.2 * s), (pe[0] + sx * 1.9 * s, pe[1] - 2.3 * s, pe[2] - 3.4 * s), 0.38 * s), -g.z), 0.15 * s)
        t = smin(t, np.maximum(np.abs(np.sqrt((g.x - pe[0]) ** 2 + ((g.y - pe[1] - 0.4 * s) * 1.1) ** 2) - 1.6 * s) - 0.3 * s, np.maximum(pe[2] - 0.8 * s - g.z, g.z - pe[2] - 0.6 * s)), 0.2 * s)
    return t


def calca(g, J, e=0.3, bainha=None, larga=0.0):
    """calça: coxas, canelas e quadril inflados; bainha na fração `bainha` da canela (None = até o tornozelo)."""
    s = J["s"]
    P = partes(g, J, e=(e + larga) * s)
    c = smin(P["gluteo"], np.maximum(P["tronco"], np.maximum(J["pelve"][2] - 3.0 * s - g.z, g.z - J["pelve"][2] - 1.3 * s)), 0.6 * s)
    for lado in ("e", "d"):
        j, a = J["joelho_" + lado], J["pe_" + lado]
        perna = smin(P["coxa_" + lado], np.maximum(P["canela_" + lado], trecho(g, j, a, -0.2, bainha if bainha is not None else 0.92)), 0.7 * s)
        c = smin(c, perna, 0.9 * s)
        # vincos atrás do joelho e franzido acima da bota
        r_j = np.sqrt((g.x - j[0]) ** 2 + (g.y - j[1]) ** 2 + (g.z - j[2]) ** 2)
        c = c + 0.12 * s * np.clip(1 - r_j / (2.0 * s), 0, 1) * np.abs(np.sin(r_j * 3.8 / s))
    return c


def bota(g, J, cano=0.55, e=0.42, sola=0.35, dobra=True):
    """botas: canela e pé inflados até a fração `cano` da canela (de baixo para cima), sola e borda do cano."""
    s = J["s"]
    P = partes(g, J, e=e * s)
    d = None
    for lado in ("e", "d"):
        j, a = J["joelho_" + lado], J["pe_" + lado]
        t0 = 1 - cano
        b = smin(np.maximum(P["canela_" + lado], trecho(g, j, a, t0, 1.2)), P["pe_" + lado], 0.5 * s)
        if dobra:
            borda = np.maximum(partes(g, J, e=(e + 0.28) * s)["canela_" + lado], trecho(g, j, a, t0, t0 + 0.07))
            b = np.minimum(b, borda)
        ps = pe_(g, a, s, e * s + 0.18 * s)
        b = np.minimum(b, np.maximum(ps, g.z - BASE - sola * s))                 # sola mais larga
        d = b if d is None else np.minimum(d, b)
    return d


def cinto(g, J, z=None, larg=0.5, fivela=True, e=0.55):
    s = J["s"]
    P = partes(g, J, e=e * s)
    z = z if z is not None else J["pelve"][2] + 1.1 * s
    c = np.maximum(smin(P["tronco"], P["gluteo"], 0.8 * s), np.abs(g.z - z) - larg * s)
    if fivela:
        p = J["pelve"]
        frente = p[1] - (3.05 if J["sexo"] == "m" else 2.75) * s - e * s
        fv = caixa(g, (p[0], frente, z), (0.6 * s, 0.3 * s, 0.62 * s), 0.12 * s)
        fv = menos(fv, caixa(g, (p[0], frente - 0.3 * s, z), (0.32 * s, 0.4 * s, 0.32 * s), 0.05 * s))
        c = np.minimum(c, fv)
    return c


def bolsa(g, J, lado="d", ang=0.0, tam=1.0, z=None):
    """bolsinha presa no cinto, no ângulo `ang` (graus a partir da frente, para o lado)."""
    s = J["s"]
    p = J["pelve"]
    z = z if z is not None else p[2] + 0.4 * s
    a = np.radians(ang) * (1 if lado == "d" else -1)
    r = 3.5 * s
    c = (p[0] + r * np.sin(a), p[1] - r * np.cos(a) * 0.75, z)
    u, v, w = local(g, c, (0, 0, 1), plano=(np.cos(a), np.sin(a) * 0.75, 0))
    b = caixa_l(u, v, w, (0, 0, 0), (0.75 * s * tam, 0.45 * s * tam, 0.8 * s * tam), 0.22 * s)
    aba = caixa_l(u, v, w, (0, -0.05 * s, 0.6 * s * tam), (0.8 * s * tam, 0.52 * s * tam, 0.22 * s), 0.1 * s)
    return np.minimum(b, aba)


def colete_tatico(g, J, e=0.95):
    """colete tático: tronco grosso até a cintura, com bolsos de carregador e alças."""
    s = J["s"]
    t = np.maximum(partes(g, J, e=e * s)["tronco"], J["cintura"][2] - 1.2 * s - g.z)
    t = np.maximum(t, g.z - J["ombro_e"][2] - 0.9 * s)
    pe = J["pescoco"]
    t = menos(t, capsula(g, (pe[0], pe[1] - 0.3 * s, pe[2] - 1.8 * s), (pe[0], pe[1] - 0.3 * s, pe[2] + 3 * s), 1.6 * s), 0.3 * s)
    for lado in ("e", "d"):                                                       # cava das mangas
        o = J["ombro_" + lado]
        t = menos(t, esfera(g, (o[0] * 1.12, o[1], o[2] - 1.3 * s), 1.4 * s), 0.3 * s)
    c = J["cintura"]
    yf = c[1] - (2.0 + e) * s
    for sx in (-1.75, 0.0, 1.75):                                                  # três porta-carregadores
        b = caixa(g, (c[0] + sx * s, yf - 0.35 * s, c[2] + 0.4 * s), (0.75 * s, 0.55 * s, 1.0 * s), 0.18 * s)
        b = np.minimum(b, caixa(g, (c[0] + sx * s, yf - 0.45 * s, c[2] + 1.35 * s), (0.8 * s, 0.6 * s, 0.22 * s), 0.08 * s))
        t = np.minimum(t, b)
    pc = J["peito"]
    t = np.minimum(t, caixa(g, (pc[0] - 1.8 * s, pc[1] - (2.6 + e) * s, pc[2] + 0.6 * s), (0.7 * s, 0.45 * s, 0.7 * s), 0.15 * s))   # bolso do rádio
    t = np.minimum(t, caixa(g, (pc[0] + 1.6 * s, pc[1] - (2.65 + e) * s, pc[2] + 1.0 * s), (0.9 * s, 0.2 * s, 0.45 * s), 0.08 * s))  # emblema
    # costura das bordas e alças sobre os ombros
    for lado in ("e", "d"):
        o = vec(J["ombro_" + lado])
        t = np.minimum(t, np.maximum(partes(g, J, e=(e + 0.15) * s)["tronco"], np.maximum(np.abs(g.x - o[0] * 0.55) - 0.75 * s, np.maximum(J["peito"][2] + 1.2 * s - g.z, g.z - J["ombro_e"][2] - 1.0 * s))))
    return t


def sobretudo(g, J, e=0.4, comp=0.55, aberto=1.1):
    """casaco longo: tronco com lapela, abas até a fração `comp` da canela, aberto na frente."""
    s = J["s"]
    t = tronco_veste(g, J, e=e, z_barra=J["pelve"][2] - 1.0 * s, gola="lapela", aberto=aberto)
    p = _v(J["pelve"])
    zb = J["joelho_e"][2] - comp * 6.5 * s
    zt = p[2] + 0.5 * s
    tt = np.clip((zt - g.z) / (zt - zb), 0, 1)
    r = (3.3 * s + e * s) + 1.5 * s * tt
    rad = np.sqrt(((g.x - p[0]) / 1.0) ** 2 + ((g.y - p[1] - 0.2 * s) / 0.8) ** 2)
    aba = np.maximum(np.abs(rad - r + 0.25 * s) - 0.3 * s, np.maximum(zb - g.z, g.z - zt))
    aba = aba + 0.22 * s * np.abs(np.sin(np.arctan2(g.y - p[1], g.x - p[0]) * 6 + 0.5)) * tt
    aba = menos(aba, np.maximum(np.abs(g.x - p[0]) - aberto * s * (0.6 + 1.6 * tt), g.y - p[1] + 0.5 * s), 0.2 * s)     # abertura da frente
    return smin(t, aba, 0.4 * s)


def saia(g, J, z_topo=None, r_topo=None, r_chao=None, comp=1.0, dobras=11, rasgada=False, aberta=0.0):
    """saia/manto em sino da cintura até `comp` (1 = chão)."""
    s = J["s"]
    p = _v(J["pelve"])
    zt = z_topo if z_topo is not None else p[2] + 1.6 * s
    zb = BASE + 0.25 + (1 - comp) * 14 * s
    rt = r_topo if r_topo is not None else 3.2 * s
    rc = r_chao if r_chao is not None else 5.6 * s
    t = np.clip((zt - g.z) / max(zt - zb, 1e-3), 0, 1)
    r = rt + (rc - rt) * t ** 0.85
    rad = np.sqrt(((g.x - p[0]) / 1.0) ** 2 + ((g.y - p[1] - 0.2 * s) / 0.82) ** 2)
    d = np.maximum(rad - r - 0.3 * s * np.abs(np.sin(np.arctan2(g.y - p[1], g.x - p[0]) * dobras * 0.5)) * t, np.maximum(zb - g.z, g.z - zt))
    if rasgada:
        d = np.maximum(d, zb + 1.2 * s * np.clip(ruido_cel(g, 1.4, 31), 0, None) - g.z)
    if aberta:
        d = menos(d, np.maximum(np.abs(g.x - p[0]) - aberta * s * t, g.y - p[1] + 0.5 * s), 0.2 * s)
    return d


def capa(g, J, comp=1.0, larg=1.0, vento=0.0, capuz=False):
    """capa presa nos ombros caindo pelas costas, com volume e dobras verticais."""
    s = J["s"]
    oe, od = _v(J["ombro_e"]), _v(J["ombro_d"])
    cx = (oe[0] + od[0]) / 2
    zt = max(oe[2], od[2]) + 0.8 * s
    zb = BASE + 0.4 + (1 - comp) * 14 * s
    t = np.clip((zt - g.z) / (zt - zb), 0, 1)
    meia = (abs(od[0] - oe[0]) / 2 + 1.2 * s) * (1 + 0.6 * t) * larg
    yc = 1.9 * s + (2.6 + 3.0 * vento) * s * t ** 1.3
    casca = np.abs(g.y - yc - 0.15 * s * np.sin((g.x - cx) * 1.5 / s) * t) - 0.3 * s
    d = np.maximum(casca, np.maximum(np.abs(g.x - cx) - meia, np.maximum(zb - g.z, g.z - zt)))
    d = d + 0.25 * s * np.abs(np.sin((g.x - cx) * 1.25 / s + 0.4)) * t
    # gola caindo sobre os ombros
    pe = _v(J["pescoco"])
    gola = np.maximum(np.abs(np.sqrt((g.x - pe[0]) ** 2 + ((g.y - pe[1] - 0.3 * s) * 1.2) ** 2) - 2.2 * s) - 0.35 * s, np.maximum(zt - 1.6 * s - g.z, g.z - zt - 0.2 * s))
    d = smin(d, gola, 0.5 * s)
    if capuz:
        d = smin(d, capuz_caido(g, J), 0.4 * s)
    return d


def capuz_caido(g, J):
    s = J["s"] * 1.12
    h = _v(J["cabeca"])
    c = h + _v((0, 2.0 * s, -2.9 * s))
    dobra = np.abs(elipsoide(g, tuple(c), (2.3 * s, 1.15 * s, 1.0 * s))) - 0.28 * s
    dobra = np.maximum(dobra, np.maximum(-(g.y - h[1] - 0.9 * s), g.z - c[2] - 0.75 * s))
    return dobra + 0.1 * s * np.abs(np.sin(np.arctan2(g.z - c[2], g.x - c[0]) * 4))


def capuz(g, J, fundo=0.0):
    """capuz levantado cobrindo a cabeça (rosto na sombra); fundo > 0 deixa o rosto mais escondido."""
    s = J["s"] * 1.12
    h = _v(J["cabeca"])
    R = np.array(mul(rot_z(J.get("giro", 0) + J.get("cabeca_giro", 0)), rot_x(-J.get("cabeca_inclina", 0))))
    gh = Vista(g, tuple(h), R)
    X, Y, Z = gh.x - h[0], gh.y - h[1], gh.z - h[2]
    cap = np.abs(elip_l(X, Y - 0.5 * s, Z - 0.3 * s, 2.7 * s, 3.0 * s, 2.85 * s)) - 0.3 * s
    abertura = -(Y + (2.1 - fundo) * s - 0.7 * s * np.clip((-Z + 1.8 * s) / (4 * s), 0, 1))
    cap = np.maximum(cap, abertura)
    cap = smin(cap, capsula_l(X, Y, Z, (0, 2.3 * s, 2.3 * s), (0, 3.4 * s, 0.8 * s), 0.6 * s, 0.25 * s), 0.4 * s)
    cap = cap + 0.12 * s * np.abs(np.sin(np.arctan2(Z, X) * 5))
    return np.maximum(cap, -2.8 * s - Z)


# ------------------------------------------------------------------ armadura
def couraca(g, J, e=0.75, faixas=3):
    """peitoral de metal com borda, quilha e faixas articuladas na barriga."""
    s = J["s"]
    P = partes(g, J, e=e * s, peso=1.05)
    zb = J["pelve"][2] + 0.4 * s
    t = np.maximum(P["tronco"], zb - g.z)
    t = np.maximum(t, g.z - J["ombro_e"][2] - 0.6 * s)
    pe = J["pescoco"]
    t = menos(t, capsula(g, (pe[0], pe[1] - 0.3 * s, pe[2] - 1.2 * s), (pe[0], pe[1] - 0.3 * s, pe[2] + 3 * s), 1.45 * s), 0.25 * s)
    for lado in ("e", "d"):
        o = J["ombro_" + lado]
        t = menos(t, esfera(g, (o[0] * 1.05, o[1], o[2] - 1.0 * s), 1.6 * s), 0.25 * s)
    c = J["cintura"]
    for k in range(faixas):
        zz = zb + (0.85 + 1.0 * k) * s
        t = menos(t, np.maximum(np.abs(g.z - zz) - 0.07 * s, -(t + 0.2 * s)), 0.04 * s)
    pc = J["peito"]
    t = smin(t, np.maximum(capsula(g, (pc[0], pc[1] - 3.3 * s, pc[2] + 1.6 * s), (pc[0], pc[1] - 2.8 * s, zb + 3.6 * s), 0.25 * s), t - 0.28 * s), 0.1 * s)
    return t


def ombreira(g, J, lado, r=2.0, camadas=3, espinho=False):
    """ombreira em lamelas sobrepostas."""
    s = J["s"]
    o = _v(J["ombro_" + lado])
    sx = -1 if lado == "e" else 1
    d = None
    for k in range(camadas):
        c = o + _v((sx * (0.35 + 0.3 * k) * s, 0, (0.75 - 0.85 * k) * s))
        e = np.maximum(np.abs(elipsoide(g, tuple(c), ((r - 0.12 * k) * s, (r * 1.08 - 0.12 * k) * s, (r - 0.15 * k) * s))) - 0.28 * s, -(g.z - c[2] + 0.75 * s))
        e = np.maximum(e, -(sx * (g.x - o[0]) + 0.6 * s))
        d = e if d is None else np.minimum(d, e)
    if espinho:
        d = smin(d, capsula(g, tuple(o + _v((sx * 0.8 * s, 0, 1.6 * s))), tuple(o + _v((sx * 1.8 * s, 0, 3.4 * s))), 0.45 * s, 0.05 * s), 0.2 * s)
    return d


def bracadeira(g, J, lado, e=0.35, ate=0.85):
    s = J["s"]
    co, w = J["cotovelo_" + lado], J["mao_" + lado]
    b = np.maximum(partes(g, J, e=e * s)["antebraco_" + lado], trecho(g, co, w, 0.3, ate))
    return b


def greva(g, J, lado, e=0.45):
    s = J["s"]
    j, a = J["joelho_" + lado], J["pe_" + lado]
    P = partes(g, J, e=e * s)
    gr = np.maximum(P["canela_" + lado], trecho(g, j, a, 0.0, 0.8))
    jo = np.maximum(np.abs(esfera(g, j, 1.45 * s)) - 0.25 * s, -(g.y - j[1] + 0.2 * s))
    return np.minimum(gr, jo)


def elmo(g, J, tipo="aberto"):
    s = J["s"] * 1.12
    h = _v(J["cabeca"])
    R = np.array(mul(rot_z(J.get("giro", 0) + J.get("cabeca_giro", 0)), rot_x(-J.get("cabeca_inclina", 0))))
    gh = Vista(g, tuple(h), R)
    X, Y, Z = gh.x - h[0], gh.y - h[1], gh.z - h[2]
    cup = np.maximum(np.abs(elip_l(X, Y - 0.2 * s, Z - 0.4 * s, 2.3 * s, 2.55 * s, 2.5 * s)) - 0.25 * s, 0.25 * s - Z + 0.0)
    if tipo == "aberto":
        cup = np.minimum(cup, np.maximum(np.abs(elip_l(X, Y - 0.2 * s, Z - 0.4 * s, 2.3 * s, 2.55 * s, 2.5 * s)) - 0.25 * s, np.maximum(-Y - 0.2 * s, -1.6 * s - Z)))
        cup = np.minimum(cup, caixa_l(X, Y, Z, (0, -2.45 * s, -0.4 * s), (0.22 * s, 0.25 * s, 1.0 * s), 0.08 * s))          # nasal
    cup = smin(cup, capsula_l(X, Y, Z, (0, -2.0 * s, 2.1 * s), (0, 2.0 * s, 2.1 * s), 0.28 * s), 0.1 * s)              # crista
    return cup


# ------------------------------------------------------------------ armas e objetos (pontos absolutos)
def espada(g, mao_, dirv, comp=12.0, larg=1.15, plano=(1, 0, 0), cabo=2.4):
    """espada: lâmina com sulco e bisel, guarda e pomo; empunhada em mao_ apontando para dirv."""
    u, v, w = local(g, mao_, dirv, plano)
    afina = np.clip((comp - w) / 2.0, 0.04, 1)
    lam = np.maximum(np.maximum(np.abs(u) - larg * 0.5 * afina, np.abs(v) - 0.24 + 0.2 * np.abs(u) / larg), np.maximum(1.1 - w, w - comp))
    lam = menos(lam, np.maximum(np.maximum(np.abs(u) - 0.1, np.abs(v) - 0.6), np.maximum(1.7 - w, w - comp * 0.72)), 0.03)
    guarda = caixa_l(u, v, w, (0, 0, 0.9), (1.75 * larg, 0.32, 0.26), 0.12)
    guarda = np.minimum(guarda, np.minimum(np.sqrt((u - 1.75 * larg) ** 2 + v ** 2 + (w - 0.9) ** 2) - 0.36, np.sqrt((u + 1.75 * larg) ** 2 + v ** 2 + (w - 0.9) ** 2) - 0.36))
    pega = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.34, np.maximum(-cabo + 0.7 - w, w - 0.8)) + 0.05 * np.abs(np.sin(w * 8))
    pomo = np.sqrt(u ** 2 + v ** 2 + (w + cabo - 0.5) ** 2) - 0.52
    return np.minimum.reduce([lam, guarda, pega, pomo])


def machado(g, mao_, dirv, comp=10.0, duplo=False, plano=(1, 0, 0), lamina=3.0):
    u, v, w = local(g, mao_, dirv, plano)
    cabo = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.4, np.maximum(-2.4 - w, w - comp - 0.6))
    lam = None
    for s_ in ((-1, 1) if duplo else (1,)):
        r = np.sqrt((u - s_ * 0.4) ** 2 + (w - comp + 1.2) ** 2)
        l = np.maximum(r - lamina, np.maximum(-s_ * u + 0.2, np.abs(w - comp + 1.2) - lamina * (0.35 + 0.65 * np.clip(s_ * u / lamina, 0, 1))))
        l = np.maximum(l, np.abs(v) - 0.38 + 0.11 * np.abs(u))
        lam = l if lam is None else np.minimum(lam, l)
    olho = caixa_l(u, v, w, (0, 0, comp - 1.2), (0.6, 0.55, 1.0), 0.15)
    return np.minimum.reduce([cabo, lam, olho])


def martelo(g, mao_, dirv, comp=9.5, plano=(1, 0, 0), cabeca=(1.9, 1.05, 1.05)):
    u, v, w = local(g, mao_, dirv, plano)
    cabo = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.36, np.maximum(-2.2 - w, w - comp))
    cab = caixa_l(u, v, w, (0, 0, comp), cabeca, 0.22)
    cab = menos(cab, np.maximum(np.abs(np.abs(u) - cabeca[0] + 0.45) - 0.08, -1), 0.03)
    return np.minimum(cabo, cab)


def maca(g, mao_, dirv, comp=7.0, plano=(1, 0, 0)):
    u, v, w = local(g, mao_, dirv, plano)
    cabo = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.36, np.maximum(-2.0 - w, w - comp))
    cab = np.sqrt(u ** 2 + v ** 2 + (w - comp) ** 2) - 1.1
    for k in range(6):
        a = k * np.pi / 3
        cab = np.minimum(cab, caixa_l(u * np.cos(a) + v * np.sin(a), -u * np.sin(a) + v * np.cos(a), w, (1.0, 0, comp), (0.45, 0.15, 1.3), 0.08))
    return np.minimum(cabo, cab)


def cajado(g, mao_, dirv, acima=8.5, abaixo=None, topo="cristal", plano=(1, 0, 0)):
    """cajado que passa pela mão; topo: cristal, galho, anel, nenhum."""
    u, v, w = local(g, mao_, dirv, plano)
    abaixo = abaixo if abaixo is not None else 20.0
    hast = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.38 - 0.06 * np.sin(w * 1.2), np.maximum(-abaixo - w, w - acima))
    if topo == "cristal":
        cr = np.maximum(np.abs(u) + np.abs(v) * 1.2 - 0.95 * np.clip((acima + 3.0 - w) / 1.5, 0, 1), np.maximum(acima - 0.2 - w, w - acima - 3.0))
        garra = np.maximum(np.abs(np.sqrt(u ** 2 + v ** 2) - 0.95) - 0.2, np.abs(w - acima - 0.2) - 0.75)
        return np.minimum.reduce([hast, cr, garra])
    if topo == "galho":
        g1 = capsula_l(u, v, w, (0, 0, acima - 1.2), (1.4, 0.3, acima + 1.9), 0.35, 0.12)
        g2 = capsula_l(u, v, w, (0, 0, acima - 0.6), (-1.1, -0.5, acima + 1.5), 0.32, 0.1)
        folhas = np.minimum(elip_l(u - 1.6, v - 0.2, w - acima - 2.2, 0.5, 0.2, 0.85), elip_l(u + 1.3, v + 0.6, w - acima - 1.8, 0.45, 0.2, 0.8))
        return np.minimum.reduce([hast, g1, g2, folhas, np.sqrt(u ** 2 + v ** 2 + (w - acima) ** 2) - 0.55])
    if topo == "anel":
        an = np.maximum(np.abs(np.sqrt(u ** 2 + (w - acima - 1.3) ** 2) - 1.3) - 0.25, np.abs(v) - 0.25)
        return np.minimum(hast, an)
    return hast


def adaga(g, mao_, dirv, comp=4.5, plano=(1, 0, 0)):
    return espada(g, mao_, dirv, comp=comp, larg=0.85, plano=plano, cabo=1.7)


def lanca(g, mao_, dirv, acima=12.0, abaixo=8.0, plano=(1, 0, 0)):
    u, v, w = local(g, mao_, dirv, plano)
    hast = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.34, np.maximum(-abaixo - w, w - acima))
    ponta = np.maximum(np.abs(u) - 0.8 * np.clip((acima + 3.2 - w) / 2.4, 0, 1) * np.clip((w - acima + 0.2) / 0.8, 0, 1), np.maximum(np.abs(v) - 0.25, np.maximum(acima - 0.2 - w, w - acima - 3.2)))
    return np.minimum(hast, ponta)


def escudo(g, centro, normal, r=4.6, tipo="redondo", emblema=None, cima=(0, 0, 1)):
    """escudo redondo (umbo e borda) ou heráldico (u = vertical), face para `normal`."""
    u, v, w = local(g, centro, normal, plano=cima)
    if tipo == "redondo":
        d2 = np.sqrt(u ** 2 + v ** 2) - r
        curva = 0.03 * (u ** 2 + v ** 2)
    else:
        d2 = np.maximum(u - r * 0.85, np.sqrt((np.abs(v) + r * 0.3) ** 2 + np.minimum(u, 0) ** 2 * 0.8) - r)
        curva = 0.025 * v ** 2
    d = np.maximum(d2, np.abs(w + curva) - 0.35)
    d = np.minimum(d, np.maximum(np.abs(d2 + 0.3) - 0.3, np.abs(w + curva - 0.15) - 0.45))                           # borda
    if tipo == "redondo":
        d = smin(d, np.sqrt(u ** 2 + v ** 2 + (w - 0.3) ** 2) - 1.15, 0.3)
        for k in range(8):
            a = k * np.pi / 4
            d = np.minimum(d, np.sqrt((u - (r - 0.95) * np.cos(a)) ** 2 + (v - (r - 0.95) * np.sin(a)) ** 2 + (w + curva - 0.4) ** 2) - 0.3)
    if emblema is not None:
        d = smin(d, np.maximum(emblema(u, v), np.abs(w + curva - 0.4) - 0.25), 0.05)
    return d


def arco(g, mao_, plano_n=(0, -1, 0), alt=18.0, puxado=0.0, dirv=(0, 0, 1)):
    """arco na mão (vertical), corda; puxado (mm) recua a corda no meio."""
    u, v, w = local(g, mao_, dirv, plano=plano_n)
    curva = 0.022 * w ** 2
    a = np.maximum(np.sqrt((u + curva - 0.0) ** 2 + v ** 2) - (0.45 - 0.014 * np.abs(w)), np.abs(w) - alt / 2)
    a = np.minimum(a, np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.55, np.abs(w) - 1.0))                                  # empunhadura
    pt = alt / 2
    cu = -0.022 * pt ** 2 - puxado * np.clip(1 - np.abs(w) / pt, 0, 1)
    corda = np.maximum(np.sqrt((u - cu) ** 2 + v ** 2) - 0.12, np.abs(w) - pt)
    return np.minimum(a, corda)


def aljava(g, J, n=5):
    s = J["s"]
    c = _v(J["peito"]) + _v((-1.2 * s, 2.8 * s, -0.5 * s))
    d = _n((0.35, 0.2, 1.0))
    u, v, w = local(g, c, d)
    q = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.95 * s, np.abs(w) - 3.3 * s)
    for k in range(n):
        a = k * 2 * np.pi / n
        q = np.minimum(q, capsula_l(u, v, w, (0.45 * s * np.cos(a), 0.45 * s * np.sin(a), 3.0 * s), (0.5 * s * np.cos(a), 0.5 * s * np.sin(a), 4.6 * s), 0.12 * s))
        q = np.minimum(q, elip_l(u - 0.5 * s * np.cos(a), v - 0.5 * s * np.sin(a), w - 4.5 * s, 0.35 * s, 0.08 * s, 0.6 * s))
    return q


def livro(g, centro, normal, larg=2.8, alt=3.6, esp=1.0, aberto=False, cima=(0, 0, 1)):
    u, v, w = local(g, centro, normal, plano=cima)
    if not aberto:
        d = caixa_l(u, v, w, (0, 0, 0), (alt / 2, larg / 2, esp / 2), 0.12)
        d = np.minimum(d, caixa_l(u, v, w, (0, -larg / 2, 0), (alt / 2 + 0.08, 0.15, esp / 2 + 0.08), 0.08))
        return d
    pag = None
    for sgn in (-1, 1):
        c = caixa_l(u, v - sgn * larg * 0.5, w - 0.15 * np.abs(v), (0, 0, 0), (alt / 2, larg / 2, 0.25), 0.1)
        pag = c if pag is None else np.minimum(pag, c)
    return pag


def pistola(g, mao_, dirv, plano=(0, 0, 1)):
    u, v, w = local(g, mao_, dirv, plano)
    cano = caixa_l(u, v, w, (0.85, 0, 1.9), (0.45, 0.33, 2.4), 0.12)
    pega = caixa_l(u, v, w, (-0.25, 0, -0.1), (0.85, 0.3, 0.5), 0.18)
    guarda = np.maximum(np.abs(np.sqrt((u - 0.1) ** 2 + (w - 0.6) ** 2) - 0.45) - 0.1, np.abs(v) - 0.12)
    return np.minimum.reduce([cano, pega, guarda])


def escopeta(g, mao_d, mao_e):
    """escopeta segura com a mão de trás em mao_d (gatilho) e a da frente em mao_e (telha)."""
    a, b = _v(mao_d), _v(mao_e)
    dirv = _n(b - a)
    u, v, w = local(g, tuple(a), dirv, plano=(0, 0, 1))
    L = float(np.linalg.norm(b - a))
    comp = L + 6.5
    cano = np.maximum(np.sqrt((u - 0.8) ** 2 + v ** 2) - 0.58, np.maximum(1.0 - w, w - comp))
    cano = menos(cano, np.maximum(np.sqrt((u - 0.8) ** 2 + v ** 2) - 0.3, comp - 0.6 - w), 0.02)
    deposito = np.maximum(np.sqrt((u + 0.05) ** 2 + v ** 2) - 0.45, np.maximum(2.0 - w, w - comp + 2.0))
    caixa_ = caixa_l(u, v, w, (0.3, 0, 0.9), (0.95, 0.55, 1.9), 0.2)
    coronha = caixa_l(u, v, w, (-0.75, 0, -2.6), (1.25, 0.55, 2.5), 0.4)
    coronha = menos(coronha, caixa_l(u, v, w, (-1.6, 0, -1.6), (0.6, 0.8, 0.9), 0.3), 0.3)
    telha = np.maximum(np.sqrt((u + 0.05) ** 2 + v ** 2) - 0.85, np.abs(w - L) - 1.6) + 0.07 * (np.abs(np.mod(w, 0.45) - 0.22) < 0.07)
    guarda = np.maximum(np.abs(np.sqrt((u + 0.55) ** 2 + (w - 0.2) ** 2) - 0.55) - 0.12, np.abs(v) - 0.15)
    return np.minimum.reduce([cano, deposito, caixa_, coronha, telha, guarda])


def faca(g, mao_, dirv, comp=4.5, plano=(1, 0, 0)):
    """facão: lâmina larga de um fio e cabo."""
    u, v, w = local(g, mao_, dirv, plano)
    lam = np.maximum(np.maximum(u - 0.6, -u - 0.6 + 0.65 * np.clip((w - comp + 1.6) / 1.6, 0, 1)), np.maximum(np.abs(v) - 0.2 + 0.1 * (u + 0.6), np.maximum(0.7 - w, w - comp)))
    pega = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.36, np.maximum(-1.8 - w, w - 0.7))
    return np.minimum(lam, pega)


def lanterna(g, mao_, dirv, plano=(0, 0, 1)):
    u, v, w = local(g, mao_, dirv, plano)
    corpo_ = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.48, np.maximum(-1.2 - w, w - 2.0))
    cab = np.maximum(np.sqrt(u ** 2 + v ** 2) - (0.5 + 0.35 * np.clip((w - 1.6) / 1.0, 0, 1)), np.maximum(1.6 - w, w - 3.0))
    return np.minimum(corpo_, cab)


def camera(g, centro, normal, cima=(0, 0, 1)):
    u, v, w = local(g, centro, normal, plano=cima)
    c = caixa_l(u, v, w, (0, 0, 0), (1.1, 1.7, 0.75), 0.25)
    lente = np.maximum(np.sqrt(u ** 2 + v ** 2) - 0.75, np.maximum(-w, w - 1.6))
    flash = caixa_l(u, v, w, (1.25, -1.0, 0), (0.25, 0.5, 0.5), 0.1)
    return np.minimum.reduce([c, lente, flash])


def vela(g, base_, alt=2.0, r=0.42):
    x, y, z = base_
    v = np.maximum(np.sqrt((g.x - x) ** 2 + (g.y - y) ** 2) - r, np.maximum(z - g.z, g.z - z - alt))
    ch = smin(elipsoide(g, (x, y, z + alt + 0.55), (0.3, 0.3, 0.45)), capsula(g, (x, y, z + alt + 0.6), (x, y, z + alt + 1.35), 0.2, 0.04), 0.15)
    return np.minimum(v, ch)


# ------------------------------------------------------------------ base
def base(g, r=12.5, tipo="pedra", semente=1):
    """base redonda de 25 mm com chão: pedra (lajes), terra, asfalto, madeira, neve."""
    rad = np.sqrt(g.x ** 2 + g.y ** 2)
    d = np.maximum(rad - r, np.maximum(-g.z, g.z - BASE))
    d = smax(d, g.z - BASE, 0.5)
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


def rodar_mini(arquivo, classe, campo_de, mn=MN_MINI, mx=MX_MINI, passo_padrao=0.08):
    """campo_de(sexo) -> função campo(g). Gera <classe>_m e <classe>_f (ou só um: --m / --f) em stl/."""
    passo, _ = args(passo_padrao)
    sexos = [s for s in ("m", "f") if f"--{s}" in sys.argv] or ["m", "f"]
    for sx in sexos:
        r = esculpir(campo_de(sx), mn, mx, passo, saida(arquivo, f"{classe}_{sx}", False), suaviza=2, min_area=0.3, vox=float(os.environ.get("VOX", 5e6)))
        print(classe, sx, {k: v[1] for k, v in r.items()}, flush=True)
