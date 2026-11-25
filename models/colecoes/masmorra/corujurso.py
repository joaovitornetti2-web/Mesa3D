"""Corujurso – filhote de corujurso (criatura do SRD 5.1) em estilo chibi: corpo de urso fofo, cara de coruja
com disco facial, bico e olhões, orelhinhas de urso e tufos de pena, bracinhos com garras e asinhas nas costas.
Cerca de 55 mm, base redonda de 32 mm. Cores: c1 pelo, c2 pupilas e garras, c3 disco facial e brilho, c4 bico.
Imprime em pé, sem suporte."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base import *

passo, IMP = args(0.22)
g = Grade((-30, -26, 0), (30, 26, 62), passo)
X, Y, Z = g.x, g.y, g.z
rr = ruido(g, 0.9, 3)

base = cilindro(g, (0, 0, 0), 16, 3.2, 1.2)
corpo = elipsoide(g, (0, 1, 19), (14.5, 13, 15))
cabeca = elipsoide(g, (0, -1, 40), (15.5, 13.5, 13))
corpo = smin(corpo, cabeca, 5)
# barriga de penas: escamas suaves (ondas) na frente
pena = np.sin(X * 1.1) * np.sin((Z - 4) * 0.9) * 0.35
corpo = corpo + np.where(Y < -6, pena, 0) + rr * 0.08
# orelhas de urso
for sx in (-1, 1):
    orelha = elipsoide(g, (sx * 11, 1, 51), (4.6, 3.2, 4.6))
    corpo = smin(corpo, orelha, 2)
    corpo = menos(corpo, elipsoide(g, (sx * 11, -1.6, 51.5), (2.6, 1.6, 2.8)), 0.6)
# tufos de pena em cima (sobrancelhas de coruja)
for sx in (-1, 1):
    corpo = smin(corpo, capsula(g, (sx * 4, -6, 50), (sx * 9.5, -4.5, 55.5), 2.6, 0.6), 1.5)
# pés com dedos
for sx in (-1, 1):
    pe = elipsoide(g, (sx * 6.5, -4, 5.2), (5.5, 7, 3.6))
    corpo = smin(corpo, pe, 2)
# braços
garras = None
for sx in (-1, 1):
    braco = capsula(g, (sx * 12, -2, 27), (sx * 9, -11, 17), 4.6, 3.8)
    corpo = smin(corpo, braco, 2.5)
    for k in (-1, 0, 1):
        gr = capsula(g, (sx * (9 + k * 2.2), -13.5, 16), (sx * (9 + k * 2.4), -15.8, 13.2), 1.1, 0.35)
        garras = gr if garras is None else np.minimum(garras, gr)
    for k in (-1, 0, 1):
        gr = capsula(g, (sx * (6.5 + k * 2.2), -10.5, 4), (sx * (6.5 + k * 2.5), -12.2, 2.4), 1.0, 0.4)
        garras = np.minimum(garras, gr)
# asinhas nas costas
for sx in (-1, 1):
    asa = elipsoide(Vista(g, (sx * 11, 9, 26), rot_y(sx * 25)), (sx * 11, 9, 26), (3, 6.5, 10))
    corpo = smin(corpo, asa, 2)
# disco facial (coração de coruja): duas elipses que se fundem
disco = smin(elipsoide(g, (-5.3, -12.2, 40), (6.6, 3.0, 7.2)), elipsoide(g, (5.3, -12.2, 40), (6.6, 3.0, 7.2)), 1.2)
olhos_b, pupilas = None, None
for sx in (-1, 1):
    ob = esfera(g, (sx * 5.3, -13.8, 41), 4.2)
    pu = esfera(g, (sx * 5.0, -16.6, 40.7), 2.4)
    br = esfera(g, (sx * 4.0, -18.3, 42.2), 0.75)
    olhos_b = ob if olhos_b is None else np.minimum(olhos_b, ob)
    pupilas = pu if pupilas is None else np.minimum(pupilas, pu)
    pupilas = menos(pupilas, br)
bico = smin(elipsoide(g, (0, -15.4, 36.4), (2.6, 2.6, 3.2)), capsula(g, (0, -16.5, 36), (0, -16.6, 32.6), 1.6, 0.5), 1.0)
claro = np.minimum(disco, menos(olhos_b, pupilas))
tudo = np.minimum.reduce([smin(corpo, base, 1.5), disco, olhos_b, bico, garras])
tudo = np.maximum(tudo, -Z)
partes = dividir(tudo, {"c4": bico, "c2": np.minimum(np.maximum(pupilas, olhos_b), garras), "c3": claro})
for k, v in exportar(g, partes, saida(__file__, "corujurso", IMP), faces=None).items():
    print(k, v)
