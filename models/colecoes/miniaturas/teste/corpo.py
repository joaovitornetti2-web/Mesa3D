"""teste de anatomia: corpo nu + cabeça em pose neutra."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figura import *


def campo_de(sexo):
    def campo(g):
        J = esqueleto(sexo, peso_d=0.65)
        b = corpo(g, J)
        cab, cabelo = cabeca(g, J, cabelo="curto" if sexo == "m" else "rabo")
        fig = np.minimum.reduce([b, cab] + ([cabelo] if cabelo is not None else []))
        return montar({"c1": fig, "c3": base(g, tipo="pedra")}, ("c3",))
    return campo


if __name__ == "__main__":
    rodar_mini(__file__, "corpo", campo_de)
