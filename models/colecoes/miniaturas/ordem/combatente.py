"""Combatente (Ordem Paranormal) – agente de linha de frente da Ordo Realitas: jaqueta de gola alta, colete tático
com porta-carregadores, calça cargo, coturnos e cinto com bolsas; escopeta em posição de pronto, facão na coxa.
Versões masculina e feminina, escala 28–32 mm, base de 25 mm com asfalto rachado.
Cores: c1 figura, c2 armas, c3 base."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figura import *


def campo_de(sexo):
    def campo(g):
        S = 0.95 if sexo == "f" else 1.0
        J = esqueleto(sexo, giro=-18, cabeca_giro=10, peso_d=0.35,
                      mao_d=(2.0 * S, -2.4 * S, BASE + 17.8 * S), cotovelo_d=(1.0, 0.7, -0.2),
                      mao_e=(-1.0 * S, -6.9 * S, BASE + 19.6 * S), cotovelo_e=(-0.6, 0.0, -1.0),
                      pe_e=(-2.2 * S, -2.2 * S, BASE + 1.05 * S), pe_d=(2.5 * S, 1.6 * S, BASE + 1.05 * S))
        P = partes(g, J)
        cab, cabelo = cabeca(g, J, cabelo="curto" if sexo == "m" else "rabo", barba="cavanhaque" if sexo == "m" else None,
                             expressao="bravo")
        pele = np.minimum.reduce([P["pescoco"], P["mao_e"], P["mao_d"], cab])
        jaq = smin(tronco_veste(g, J, e=0.35, z_barra=J["pelve"][2] - 1.2 * S, gola="alta"),
                   np.minimum(manga(g, J, "e", ate=0.9), manga(g, J, "d", ate=0.9)), 0.4)
        roupa = np.minimum.reduce([jaq, colete_tatico(g, J), calca(g, J, e=0.28), bota(g, J, cano=0.42),
                                   cinto(g, J, e=0.7), bolsa(g, J, "d", 70), bolsa(g, J, "e", 85, tam=0.9)])
        # bolsos cargo nas coxas
        for lado, sx in (("e", -1), ("d", 1)):
            q, j = vec(J["quadril_" + lado]), vec(J["joelho_" + lado])
            c = q + (j - q) * 0.55 + vec((sx * 1.85 * S, 0, 0))
            roupa = np.minimum(roupa, massa(g, tuple(q), tuple(j), 0.55, (0.55 * S, 1.2 * S, 1.3 * S), desl=(sx * 1.9 * S, 0, 0)))
        fig = np.minimum.reduce([pele, cabelo, roupa])
        arma = escopeta(g, J["mao_d"], J["mao_e"])
        q = vec(J["quadril_e"])
        fac = faca(g, tuple(q + vec((-2.3 * S, -0.3, -1.5 * S))), (0.05, -0.15, -1), comp=4.0, plano=(0, 1, 0))
        bainha = massa(g, tuple(q + vec((-2.2 * S, 0, -1.0 * S))), tuple(q + vec((-2.2 * S, 0.0, -6.0 * S))), 0.55, (0.35 * S, 0.75 * S, 2.3 * S))
        bs = base(g, tipo="asfalto", semente=3)
        return montar({"c1": np.minimum(fig, bainha), "c2": np.minimum(arma, fac), "c3": bs}, ("c3", "c2"))
    return campo


if __name__ == "__main__":
    rodar_mini(__file__, "combatente", campo_de)
