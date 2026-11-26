"""Combatente (Ordem Paranormal) – agente da Ordo Realitas de linha de frente: colete tático com bolsos, jaqueta,
calça e coturnos, escopeta empunhada na diagonal e facão no cinto. Versões masculina e feminina, escala 28–32 mm,
base de 25 mm com asfalto rachado. Cores: c1 figura, c2 armas, c3 base."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figura import *


def campo_de(sexo):
    def campo(g):
        S = 0.96 if sexo == "f" else 1.0
        J = esqueleto(sexo,                                   # escopeta pronta, apontada para a frente e para baixo
                      mao_d=(2.0 * S, -3.8, BASE + 19.2 * S), cotovelo_d=(4.6 * S, -0.8, BASE + 20.0 * S),
                      mao_e=(-0.8 * S, -7.4, BASE + 20.6 * S), cotovelo_e=(-3.6 * S, -4.4, BASE + 22.0 * S),
                      pe_e=(-2.3 * S, -2.4, BASE + 0.9), pe_d=(2.8 * S, 1.8, BASE + 0.9))
        b = corpo(g, J, musculo=1.05 if sexo == "m" else 1.0)
        cab, cabelo = cabeca(g, J, cabelo="raspado" if sexo == "m" else "rabo", barba="cavanhaque" if sexo == "m" else None)
        roupa = np.minimum.reduce([jaqueta(g, J, b, comp=1.0, aberta=False, esp=0.45) + vincos(g, J), colete(g, J, b, esp=0.9),
                                   calca(g, J, b, folgada=0.15) + vincos(g, J), botas(g, J, b, esp=0.35), cinto(g, J)])
        fig = np.minimum.reduce([b, cab, cabelo, roupa])
        dirv = np.array(J["mao_e"]) - np.array(J["mao_d"])
        arma = espingarda(g, J["mao_d"], dirv, comp=12.5, plano=(0, 1, 0))
        fac = faca(g, (-3.3 * S, -0.6, J["pelve"][2] - 0.2), (0, -0.25, -1), comp=4.2, plano=(0, 1, 0))
        bs = base(g, tipo="asfalto", semente=3)
        return montar({"c1": fig, "c2": np.minimum(arma, fac), "c3": bs}, ("c3", "c2"))
    return campo


if __name__ == "__main__":
    rodar_mini(__file__, "combatente", campo_de)
