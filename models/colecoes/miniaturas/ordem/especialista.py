"""Especialista (Ordem Paranormal) – investigadora/investigador da Ordo Realitas: sobretudo aberto com lapela,
camisa, calça e sapatos; lanterna apontada para a frente numa mão e câmera fotográfica na outra, bolsa de
ombro com a alça cruzando o peito. Escala 28–32 mm, base de 25 mm com lajes de pedra.
Cores: c1 figura, c2 equipamento, c3 base."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figura import *


def campo_de(sexo):
    def campo(g):
        S = 0.95 if sexo == "f" else 1.0
        J = esqueleto(sexo, giro=12, cabeca_giro=-14, cabeca_inclina=6, peso_d=0.7,
                      mao_e=(-3.6 * S, -6.2 * S, BASE + 21.0 * S), cotovelo_e=(-1.0, 0.4, -0.6),
                      mao_d=(3.0 * S, -3.4 * S, BASE + 22.6 * S), cotovelo_d=(1.0, 0.2, -1.0),
                      pe_e=(-2.4 * S, -1.6 * S, BASE + 1.05 * S), pe_d=(1.9 * S, 1.2 * S, BASE + 1.05 * S))
        P = partes(g, J)
        cab, cabelo = cabeca(g, J, cabelo="topete" if sexo == "m" else "longo", expressao="seria")
        pele = np.minimum.reduce([P["pescoco"], P["mao_e"], P["mao_d"], cab])
        camisa = tronco_veste(g, J, e=0.22, z_barra=J["pelve"][2] - 0.8 * S, gola="alta")
        casaco = smin(sobretudo(g, J, e=0.5, comp=0.45, aberto=1.2), np.minimum(manga(g, J, "e", e=0.45, ate=0.88, punho=0.3),
                                                                             manga(g, J, "d", e=0.45, ate=0.88, punho=0.3)), 0.4)
        sapato = bota(g, J, cano=0.12, e=0.3, dobra=False)
        roupa = np.minimum.reduce([camisa, casaco, calca(g, J, e=0.26), sapato, cinto(g, J, e=0.35)])
        # bolsa a tiracolo: alça do ombro direito ao quadril esquerdo, bolsa no quadril esquerdo
        od, qe = vec(J["ombro_d"]), vec(J["quadril_e"])
        alca = np.minimum(np.maximum(partes(g, J, e=0.95 * S)["tronco"], capsula(g, tuple(od + vec((-0.4 * S, 0, 0.5 * S))), tuple(qe + vec((-0.5 * S, 0, 1.4 * S))), 0.4 * S)),
                          caixa(g, tuple(qe + vec((-2.2 * S, -0.4 * S, 0.2 * S))), (0.7 * S, 1.6 * S, 1.3 * S), 0.35 * S))
        fig = np.minimum.reduce([pele, cabelo, roupa, alca])
        lan = lanterna(g, J["mao_e"], vec(J["mao_e"]) - vec(J["cotovelo_e"]) + vec((0, -0.4, 0.3)))
        cam = camera(g, tuple(vec(J["mao_d"]) + vec((-0.3 * S, -0.9 * S, 0.5 * S))), (0.2, -1, 0.1))
        bs = base(g, tipo="pedra", semente=5)
        return montar({"c1": fig, "c2": np.minimum(lan, cam), "c3": bs}, ("c3", "c2"))
    return campo


if __name__ == "__main__":
    rodar_mini(__file__, "especialista", campo_de)
