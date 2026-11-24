"""Pedrinha Sonolenta – seixo liso de bolso que cochila enrolado num cobertorzinho, com touquinha de dormir,
olhinhos fechados, um "z" flutuando e uma covinha no topo para o polegar.
c1 pedra · c2 rosto e "z" · c4 cobertor, touca e bochechas."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sdf import *

passo = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
g = Grade((-34, -26, 0), (34, 26, 30), passo)
X, Y, Z = g.x, g.y, g.z
pedra = elipsoide(g, (0, 0, 6), (28, 21, 12))
pedra = np.maximum(pedra, -Z)
pedra = smin(pedra, cilindro(g, (0, 0, 0), 21, 1.5, 1.2), 4)
# covinha para o polegar
pedra = menos(pedra, elipsoide(g, (4, 3, 20.5), (11, 9, 4.2)), 1.5)
pedra = pedra + 0.05 * ruido(g, 2.5, 3)
# cobertor dobrado por cima da metade de trás, com barra ondulada
th = np.arctan2(Y, X)
borda = -4 + 1.0 * np.sin(X * 0.45)
cob = np.maximum(np.abs(pedra + 0.0) - 1.2, -(Y - borda))
cob = np.maximum(np.maximum(cob, -pedra - 1.4), 2.5 - Z)
cob = smin(cob, np.maximum(capsula(g, (-28, borda, 6), (28, borda, 6), 0) if False else cob, cob), 0.1)
dobra = np.maximum(capsula(g, (-27, -3.6, 10.5), (27, -3.6, 10.5), 1.8), -Z + 1)
dobra = np.maximum(dobra, pedra - 2.2)
pedra2 = smin(np.minimum(pedra, cob), dobra, 0.8)
# rosto dormindo na frente
def fy(x, z):
    return -21 * np.sqrt(max(0, 1 - (x / 28) ** 2 - ((z - 6) / 12) ** 2))
olhos = None
for s in (-1, 1):
    x0, z0 = s * 7.5, 8.5
    pts = [(x0 + 3.2 * np.sin(t), fy(x0 + 3.2 * np.sin(t), z0 - 1.3 * np.cos(t)) - 0.5, z0 - 1.3 * np.cos(t)) for t in np.linspace(-1.25, 1.25, 7)]
    a = tubo(g, pts, [0.7] * 7)
    olhos = a if olhos is None else np.minimum(olhos, a)
boca = elipsoide(g, (0, fy(0, 4.5) - 0.3, 4.5), (1.4, 1.2, 1.1))
boch = np.minimum(elipsoide(g, (-13, fy(-13, 5.5) + 0.2, 5.5), (2.8, 1.4, 1.8)), elipsoide(g, (13, fy(13, 5.5) + 0.2, 5.5), (2.8, 1.4, 1.8)))
corpo = smin(pedra2, olhos, 0.3)
corpo = menos(corpo, boca, 0.3)
corpo = smin(corpo, boch, 0.4)
# touquinha caída de lado com pompom
touca = tubo(g, [(-13, 4, 13.0), (-14, 5, 18), (-17.5, 6, 21.5), (-21.5, 6.5, 22.0), (-24, 6.5, 20.5)], [6.2, 4.8, 3.2, 2.0, 1.2])
touca = smin(touca, toro(g, (-13, 4, 14.0), 5.8, 1.7, 1.0), 0.6)
pompom = esfera(g, (-25.2, 6.5, 19.0), 2.7)
corpo = smin(corpo, touca, 0.8)
corpo = smin(corpo, pompom, 0.5)
# "z" flutuando preso na touca
zz = np.maximum(np.abs(Y - 7) - 1.1, np.minimum.reduce([
    np.maximum(np.abs(Z - 19.6) - 0.6, np.abs(X - 15.5) - 2.2),
    np.maximum(np.abs(Z - 15.6) - 0.6, np.abs(X - 15.5) - 2.2),
    np.maximum(np.abs((Z - 17.6) - 0.9 * (X - 15.5)) - 0.7, np.abs(X - 15.5) - 2.0)]))
corpo = smin(corpo, zz, 0.3)
corpo = np.maximum(corpo, -Z)
reg = {"c2": np.minimum.reduce([olhos - 0.1, np.maximum(boca - 0.7, -corpo - 0.8), zz - 0.1]),
       "c4": np.minimum.reduce([np.maximum(cob, -(Y - borda)) - 0.05, dobra - 0.1, touca - 0.2, boch - 0.1])}
reg = {"c3": pompom - 0.2, **reg}
for k, v_ in exportar(g, dividir(corpo, reg), os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "pedra"), faces=None).items():
    print(k, v_)
