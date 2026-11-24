"""Peças de rosto reaproveitadas pela Turma esculpida (olhos com brilho, bochechas, boca, presas)."""
import numpy as np

from sdf import *


def frente(x, z, cz, R, s=0.94, cy=0.0):
    """y da superfície frontal (-Y) de uma cabeça elíptica de raio R centrada em (0, cy, cz)."""
    return cy - s * np.sqrt(max(0.0, R * R - x * x - (z - cz) ** 2))


class Rosto:
    def __init__(self, g, cz, R, s=0.94, cy=0.0):
        self.g, self.cz, self.R, self.s, self.cy = g, cz, R, s, cy
        self.relevo, self.c2, self.c3, self.c4, self.corte = [], [], [], [], []

    def y(self, x, z):
        return frente(x, z, self.cz, self.R, self.s, self.cy)

    def olho(self, x, z, rx, rz, olhar=(0.0, 0.0)):
        g = self.g
        y0 = self.y(x, z) + 0.9
        self.relevo.append(elipsoide(g, (x, y0, z), (rx, 1.9, rz)))
        self.c2.append(elipsoide(g, (x, y0, z), (rx, 6.0, rz)))
        bx, bz = x + olhar[0], z + olhar[1]
        self.c3.append(esfera(g, (bx + rx * 0.35, y0 - 1.25, bz + rz * 0.42), max(0.55, rx * 0.3)))
        self.c3.append(esfera(g, (bx - rx * 0.28, y0 - 1.15, bz - rz * 0.38), max(0.4, rx * 0.15)))

    def bochecha(self, x, z, rx=2.6, rz=1.7):
        y0 = self.y(x, z) + 0.55
        self.relevo.append(elipsoide(self.g, (x, y0, z), (rx, 1.0, rz)))
        self.c4.append(elipsoide(self.g, (x, y0, z), (rx, 5.0, rz)))

    def sobrancelha(self, x1, z1, x2, z2, r=0.85):
        self.relevo.append(capsula(self.g, (x1, self.y(x1, z1) + 0.3, z1), (x2, self.y(x2, z2) + 0.3, z2), r, r * 0.9))

    def boca(self, x, z, rx, rz, lingua=None, reta=True):
        """boca aberta em D cavada no rosto (cor c2) com língua opcional (cor c4): lingua = (dx, dz)."""
        g = self.g
        y0 = self.y(x, z) - 0.4
        vol = elipsoide(g, (x, y0, z), (rx, 3.2, rz))
        if reta:
            vol = np.maximum(vol, -(g.z - (z + rz * 0.15)))
        self.corte.append(vol)
        self.boca_cor = elipsoide(g, (x, y0, z + 0.3), (rx + 1.0, 4.2, rz + 1.0))
        if lingua is not None:
            lx, lz = x + lingua[0], z - rz * 0.7 + lingua[1]
            lg = elipsoide(g, (lx, self.y(lx, lz) - 1.4, lz), (rx * 0.5, 2.0, rz * 0.4))
            self.relevo.append(lg)
            self.c4.append(lg - 0.1)

    def presa(self, x, z, h=2.2, r=0.9):
        g = self.g
        y0 = self.y(x, z) - 0.2
        p = capsula(g, (x, y0, z + 0.4), (x, y0 - 0.5, z - h), r, 0.25)
        self.relevo.append(p)
        self.c3.append(p - 0.05)

    def aplicar(self, corpo):
        for r in self.relevo:
            corpo = smin(corpo, r, 0.5)
        for c in self.corte:
            corpo = menos(corpo, c, 0.6)
        if hasattr(self, "boca_cor"):
            self.c2.append(np.maximum(self.boca_cor, -corpo - 0.9))
        return corpo


def juntar(lista):
    return None if not lista else np.minimum.reduce(lista) if len(lista) > 1 else lista[0]
