"""Boo, o fantasminha da Turma – versão esculpida (SDF).
Personalidade: aprendiz de mago trapalhão – chapéu torto grande demais, acena com uma mão
e segura o d20 da sorte com a outra, sobrancelha levantada e língua de fora.
Cores (AMS, 4): c1 corpo · c2 olhos/boca/faixa do chapéu · c3 brilho dos olhos/estrelinhas · c4 chapéu, d20, língua, bochechas.
Uso: python3 boo.py [passo_mm]  -> stl/boo_c1..c4.stl
"""
import sys

import numpy as np

from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.22
g = Grade((-31, -27, 0), (31, 27, 73), passo)
X, Y, Z = g.x, g.y, g.z

# ---------- corpo: cabeça + lençol que alarga, com dobras de pano ----------
HZ, HR = 33.0, 16.2
cabeca = elipsoide(g, (0, 0, HZ), (HR, HR * 0.94, HR * 0.98))
th = np.arctan2(Y, X)
rho = np.sqrt(X * X + Y * Y)
t = np.clip((29 - Z) / 24, 0, 1)                      # 0 no peito, 1 na barra
R = 12.8 + 5.4 * t ** 1.5 + (0.3 + 1.3 * t) * np.sin(5 * th + 1.3 * t + 0.8) - 0.55 * t * np.abs(np.sin(5 * th + 1.3 * t + 0.8 + 1.57)) ** 0.5
lencol = np.maximum((rho - R) * 0.8, np.maximum(Z - 30, 4.5 - Z))
corpo = smin(cabeca, lencol, 5.0)

# barra em ondas (pontas caindo) e nuvem de névoa como base
for k in range(5):
    a = np.radians(k * 72 + 30)
    corpo = smin(corpo, esfera(g, (16.5 * np.cos(a), 16.5 * np.sin(a), 5.2), 3.4), 2.5)
nevoa = cilindro(g, (0, 0, 0), 17.5, 2.6, 1.2)
for k in range(8):
    a = np.radians(k * 45 + 10)
    rr = 4.4 + 1.2 * np.sin(k * 2.1)
    nevoa = smin(nevoa, esfera(g, ((18 + 0.8 * np.sin(k * 1.7)) * np.cos(a), (18 + 0.8 * np.sin(k * 1.7)) * np.sin(a), 1.6), rr), 2.2)
corpo = smin(corpo, nevoa, 3.0)

# rabinho de fumaça que enrola atrás
cauda = tubo(g, [(0, 11, 14), (5, 17, 11), (11, 19, 14), (12, 16, 20), (8.5, 14.5, 22)], [5.0, 3.8, 2.6, 1.6, 0.8])
corpo = smin(corpo, cauda, 2.5)

# braços: um acenando, outro segurando o d20 na frente
corpo = smin(corpo, tubo(g, [(12, -1, 25), (17.5, -3, 29.5), (20.5, -4, 34)], [4.3, 3.5, 3.0]), 3.0)
mao_a = esfera(g, (21.0, -4.3, 35.6), 3.6)
corpo = smin(corpo, mao_a, 1.5)
corpo = smin(corpo, tubo(g, [(-11, -2, 23), (-12.5, -9, 21), (-9.5, -14.5, 20)], [4.2, 3.6, 3.3]), 3.0)

# textura suave de pano (dobras finas), antes dos detalhes do rosto
corpo = corpo + 0.045 * ruido(g, 2.2, 7)

# ---------- rosto ----------
def frente(x, z, r=HR, zc=HZ, s=0.94):
    return -s * np.sqrt(max(0.0, r * r - x * x - (z - zc) ** 2))

olhos, brilho = None, None
for sx, zo, alt in ((-1, 34.4, 5.4), (1, 34.8, 4.7)):        # olho esquerdo maior: expressão marota
    x0 = sx * 6.6
    y0 = frente(x0, zo) + 0.9
    o = elipsoide(g, (x0, y0, zo), (3.7, 1.9, alt))
    olhos = o if olhos is None else np.minimum(olhos, o)
    oc = elipsoide(g, (x0, y0, zo), (3.7, 6.0, alt))     # cor corta reto na superfície (borda limpa)
    olhos_cor = oc if sx == -1 else np.minimum(olhos_cor, oc)
    b = esfera(g, (x0 + 1.3, y0 - 1.2, zo + alt * 0.42), 1.15)
    b = np.minimum(b, esfera(g, (x0 - 0.9, y0 - 0.9, zo - alt * 0.35), 0.5))
    brilho = b if brilho is None else np.minimum(brilho, b)
corpo = smin(corpo, olhos, 0.6)

# sobrancelhas de massinha: uma levantada
corpo = smin(corpo, capsula(g, (-9.8, frente(-9.8, 41.6) + 0.3, 41.4), (-4.0, frente(-4.0, 43.2) + 0.3, 43.0), 0.9, 0.8), 0.8)
corpo = smin(corpo, capsula(g, (4.2, frente(4.2, 41.0) + 0.3, 41.2), (9.6, frente(9.6, 40.4) + 0.3, 40.0), 0.85, 0.8), 0.8)

# boca aberta de sorriso torto, com língua de fora
bz = 27.0
boca_vol = elipsoide(g, (0.8, frente(0.8, bz) - 0.4, bz), (4.4, 3.2, 3.0))
boca_vol = np.maximum(boca_vol, -(Z - (bz - 2.6) - 0.18 * (X - 0.8)))      # corta reto em cima (sorriso em D)
corpo = menos(corpo, boca_vol, 0.6)
boca_cor = np.maximum(elipsoide(g, (0.8, frente(0.8, bz) - 0.4, bz + 0.3), (5.4, 4.2, 4.0)), -corpo - 0.9)
lingua = elipsoide(g, (2.2, frente(2.2, bz - 2.9) - 1.6, bz - 2.9), (2.2, 2.0, 1.25))
corpo = smin(corpo, lingua, 0.5)

bochechas = None
for sx in (-1, 1):
    x0 = sx * 11.2
    b = elipsoide(g, (x0, frente(x0, 30.0) + 0.55, 30.0), (2.6, 1.0, 1.7))
    bochechas = b if bochechas is None else np.minimum(bochechas, b)
    bc = elipsoide(g, (x0, frente(x0, 30.0) + 0.55, 30.0), (2.6, 5.0, 1.7))
    bochechas_cor = bc if sx == -1 else np.minimum(bochechas_cor, bc)
corpo = smin(corpo, bochechas, 0.4)

# ---------- d20 da sorte ----------
dado = d20(g, (-7.5, -17.4, 21.5), 4.8, 0.45, rot=mul(rot_z(18), rot_x(25)))
corpo = smin(corpo, dado, 0.8)
corpo = smin(corpo, esfera(g, (-11.0, -16.0, 20.0), 2.6), 1.2)                 # mãozinha por trás do dado

# ---------- chapéu de mago torto ----------
HC = (0.5, 1.0, 46.6)
v = Vista(g, HC, mul(rot_y(-14), rot_x(9)))
aba_r = 14.2 + 0.7 * np.sin(4 * np.arctan2(v.y - HC[1], v.x - HC[0]) + 0.5)
aba = np.maximum(np.sqrt((v.x - HC[0]) ** 2 + (v.y - HC[1]) ** 2) - aba_r, np.abs(v.z - HC[2] - 0.4) - 0.5) - 0.45
cone = tubo(v, [(0.5, 1.0, 47.1), (0.8, 2.2, 52.6), (1.6, 3.8, 57.6), (4.6, 5.6, 61.8), (9.5, 5.6, 62.6), (12.3, 3.6, 60.8)],
            [8.6, 7.0, 5.2, 3.3, 1.8, 0.9])
amassado = 0.22 * np.sin(1.3 * v.z + 2 * np.arctan2(v.y, v.x))                # tecido amassado
chapeu = smin(aba, cone + amassado, 1.4)
faixa = np.maximum(toro(v, (0.5, 1.0, 49.2), 8.25, 1.25, 1.05), -chapeu - 0.05)
chapeu = smin(chapeu, faixa, 0.3)
estrelas = None
for (ex, ey, ez, er) in ((-5.6, -3.6, 54.1, 0.9), (3.2, -3.2, 57.2, 0.7), (-1.2, -2.8, 59.6, 0.55)):
    s = esfera(v, (ex, ey, ez), er)
    estrelas = s if estrelas is None else np.minimum(estrelas, s)
chapeu = smin(chapeu, estrelas, 0.2)
corpo = smin(corpo, chapeu, 0.9)

# ---------- textura de mão (argila) só no corpo e mesa plana ----------
corpo = np.maximum(corpo, -Z)

reg = {
    "c3": np.minimum(brilho - 0.05, estrelas),
    "c4": np.minimum.reduce([np.maximum(chapeu - 1.2, -(faixa - 0.08)), dado - 0.15, lingua - 0.1, bochechas_cor]),
    "c2": np.minimum(np.minimum(olhos_cor, boca_cor), faixa - 0.08),
}
partes = dividir(corpo, reg)
feitos = exportar(g, partes, "stl/boo", faces=300000)
for k, v_ in feitos.items():
    print(k, v_)
