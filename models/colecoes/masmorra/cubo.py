"""Cubo Gelatinoso Porta-Dados – o cubo de gosma (criatura do SRD 5.1) em versão fofa: bordas moles que escorrem,
olhinhos, sorriso e o que ele engoliu pela masmorra (espada atravessada, caveira e moedas meio afundadas).
Em cima, um poço onde os dados "afundam". Cerca de 62 × 62 × 60 mm.
Cores: c1 gosma, c2 lâmina e pupilas, c3 caveira e olhos, c4 cabo da espada e moedas. Em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.14)
MN, MX = (-44, -40, 0), (44, 38, 70)


def campo(g):
    X, Y, Z = g.x, g.y, g.z
    A = 29.0
    rr = ruido(g, 3.0, 11)
    # cubo mole: caixa arredondada com o topo levemente afundado e laterais "barrigudas"
    cubo = caixa(g, (0, 0, 29), (A, A, 28), 9.0) + rr * 0.22
    cubo = cubo - 1.2 * np.exp(-((Z - 12) / 10) ** 2)          # barriga mole embaixo
    # escorridos descendo pelas laterais
    for (x, y, z, c) in [(-18, -A, 50, 14), (6, -A, 52, 20), (21, -A, 48, 10), (A, -10, 50, 18), (A, 14, 46, 12), (-A, 4, 50, 22), (-A, -18, 44, 9), (-8, A, 50, 16)]:
        n = np.array([np.sign(x) if abs(x) == A else 0, np.sign(y) if abs(y) == A else 0, 0.0])
        p0 = np.array([x, y, z], float) + n * 0.5
        cubo = smin(cubo, capsula(g, p0, p0 + np.array([0, 0, -c]) + n * 1.2, 2.6, 3.4), 2.2)
    # poça na base
    cubo = smin(cubo, np.maximum(cilindro(g, (0, 0, 0), A + 6, 2.4, 1.0) + rr * 0.25 + 1.5 * np.clip(ruido(g, 6.0, 12), 0, None), -Z), 3)
    # poço em cima para os dados
    poco = smin(caixa(g, (0, 0, 62), (A - 7, A - 7, 16), 8.0), esfera(g, (0, 0, 50), 1), 1) + rr * 0.3
    cubo = menos(cubo, poco, 2.0)
    # rosto: olhos e sorriso na frente
    olhos, pupilas = None, None
    for sx in (-1, 1):
        o = elipsoide(g, (sx * 9, -A - 3.0, 36), (5.2, 3.2, 6.2))
        p = esfera(g, (sx * 8.4, -A - 5.6, 35), 2.7)
        olhos = o if olhos is None else np.minimum(olhos, o)
        pupilas = p if pupilas is None else np.minimum(pupilas, p)
    boca = np.maximum(toro(Vista(g, (0, -A - 2, 27), rot_x(90)), (0, -A - 2, 27), 7, 1.4), Z - 26)
    cubo = menos(cubo, boca, 0.6)
    # espada atravessada (sai pela direita, ponta pela esquerda)
    v = Vista(g, (0, 6, 30), mul(rot_z(188), rot_y(14)))
    lamina = np.maximum(caixa(v, (-6, 6, 30), (30, 3.2, 0.9), 0.4), np.abs(v.x + 6) - 38)
    ponta = np.maximum(caixa(v, (-39, 6, 30), (4, 3.2, 0.9), 0.4), (np.abs(v.y - 6) - 3.2 * np.clip((v.x + 35) / -8 + 1, 0, 1)))
    lamina = np.minimum(lamina, ponta)
    guarda = caixa(v, (26, 6, 30), (1.6, 8, 1.6), 0.8)
    cabo = np.minimum(capsula(v, (27, 6, 30), (38, 6, 30), 1.9), esfera(v, (39.5, 6, 30), 2.8))
    cabo = np.minimum(cabo, guarda)
    # caveira saindo pela quina da frente direita
    cx, cy, cz = 21, -29, 13
    cranio = smin(esfera(g, (cx, cy, cz + 1), 7.2), elipsoide(g, (cx - 1.6, cy - 3.5, cz - 3.4), (4.6, 4, 3.6)), 2.0)
    cranio = menos(cranio, np.minimum.reduce([esfera(g, (cx - 4.6, cy - 6.2, cz), 2.1), esfera(g, (cx + 0.8, cy - 7.0, cz), 2.1),
                                              esfera(g, (cx - 1.9, cy - 7.6, cz - 2.6), 0.9)]), 0.3)
    # moedas meio afundadas
    moedas = None
    for (x, y, z, ax, ay) in [(-20, -27, 16, 70, 20), (-12, -29, 9, 80, -10), (-27, -12, 20, 15, 75), (24, 26, 18, -70, -20), (-8, 2, 55, 0, 25), (10, -6, 54, 20, -15)]:
        vm = Vista(g, (x, y, z), mul(rot_x(ax), rot_y(ay)))
        m = cilindro(vm, (x, y, z - 0.9), 4.2, 1.8, 0.5)
        m = menos(m, cilindro(vm, (x, y, z + 0.4), 2.8, 2, 0.2), 0.2)
        moedas = m if moedas is None else np.minimum(moedas, m)
    # bolhas na gosma (umas saltadas, outras furinhos), ondulação mole, osso e dentes na caveira
    bolhas_m, bolhas_f = None, None
    rng = np.random.default_rng(5)
    for k in range(70):
        lado = rng.integers(0, 5)
        a, b = rng.uniform(-A + 6, A - 6, 2)
        zz = rng.uniform(10, 54)
        p = [(a, -A - 0.3, zz), (a, A + 0.3, zz), (-A - 0.3, a, zz), (A + 0.3, a, zz), (a, b, 57.3 - 2.0)][lado]
        r = rng.uniform(0.5, 1.6)
        e = esfera(g, p, r)
        if k % 3 == 0:
            bolhas_f = e if bolhas_f is None else np.minimum(bolhas_f, e)
        else:
            bolhas_m = e if bolhas_m is None else np.minimum(bolhas_m, e)
    cubo = menos(smin(cubo, bolhas_m + 0.45, 0.6), bolhas_f, 0.3)
    cubo = cubo + 0.12 * np.sin(Z * 0.55 + 1.3 * np.sin(X * 0.2)) * np.clip(1 - np.abs(cubo) / 2, 0, 1)
    osso = np.minimum.reduce([capsula(g, (-24, 18, 30), (-12, 26, 22), 1.5),
                              esfera(g, (-24.5, 17.0, 31.2), 2.0), esfera(g, (-25.2, 19.0, 29.6), 2.0),
                              esfera(g, (-11.4, 27.2, 21.6), 2.0), esfera(g, (-12.0, 25.2, 20.2), 2.0)])
    dentes = None
    for k in range(-2, 3):
        d = caixa(g, (cx - 1.6 + k * 1.05, cy - 6.8, cz - 5.0), (0.42, 0.6, 0.85), 0.25)
        dentes = d if dentes is None else np.minimum(dentes, d)
    cranio = np.minimum(cranio, dentes)
    cranio = np.minimum(cranio, osso)
    amarelo = np.minimum(cabo, moedas)
    tudo = np.minimum.reduce([cubo, olhos, lamina, cabo, cranio, moedas])
    tudo = np.maximum(tudo, -Z)
    return tudo, {"c2": np.minimum(lamina, np.maximum(pupilas, olhos)), "c4": amarelo, "c3": np.minimum(cranio, olhos)}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "cubo", IMP)).items():
        print(k, v)
