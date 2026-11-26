"""Ocultista (Ordem Paranormal) – conjurador da Ordo Realitas: túnica longa com capuz caído, faixa na cintura,
grimório aberto numa mão e a outra erguida conjurando; a Marca de Sangue gravada no chão de pedra da base,
com duas velas acesas. Escala 28–32 mm, base de 25 mm.
Cores: c1 figura, c2 livro e velas, c3 base, c4 Marca de Sangue."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from figura import *


def campo_de(sexo):
    def campo(g):
        S = 0.95 if sexo == "f" else 1.0
        J = esqueleto(sexo, giro=-8, cabeca_giro=-6, cabeca_inclina=10, peso_d=0.4,
                      mao_e=(-2.6 * S, -4.9 * S, BASE + 20.4 * S), cotovelo_e=(-1.0, 0.6, -0.8),
                      mao_d=(4.6 * S, -4.2 * S, BASE + 28.4 * S), cotovelo_d=(1.0, 0.5, -1.0),
                      pe_e=(-1.8 * S, -1.2 * S, BASE + 1.05 * S), pe_d=(2.0 * S, 0.9 * S, BASE + 1.05 * S))
        J["aberta_d"] = (0.3, -1.0, 0.4)                         # mão direita aberta, palma para a frente
        P = partes(g, J)
        cab, cabelo = cabeca(g, J, cabelo="careca" if sexo == "m" else "trancas", barba="cheia" if sexo == "m" else None)
        pele = np.minimum.reduce([P["pescoco"], P["mao_e"], P["mao_d"], cab])
        tunica = tronco_veste(g, J, e=0.4, z_barra=J["pelve"][2] - 0.5 * S, decote=1.2)
        mangas = np.minimum(manga(g, J, "e", e=0.5, ate=0.75, punho=0.3), manga(g, J, "d", e=0.5, ate=0.72, punho=0.3))
        veste = saia(g, J, comp=1.0, r_topo=3.4 * S, r_chao=5.2 * S, dobras=12)
        faixa = cinto(g, J, e=0.75, larg=0.75, fivela=False)
        pontas = capsula(g, (J["pelve"][0] - 1.4 * S, J["pelve"][1] - 3.3 * S, J["pelve"][2] + 1.2 * S),
                         (J["pelve"][0] - 1.9 * S, J["pelve"][1] - 3.6 * S, J["pelve"][2] - 4.5 * S), 0.45 * S, 0.3 * S)
        roupa = np.minimum.reduce([smin(tunica, veste, 0.6), mangas, faixa, pontas, capuz_caido(g, J)])
        fig = np.minimum.reduce([pele] + ([cabelo] if cabelo is not None else []) + [roupa])
        md = vec(J["mao_e"])
        liv = livro(g, tuple(md + vec((0.4 * S, -1.4 * S, 0.9 * S))), (0.15, -0.55, 1.0), larg=2.0, alt=3.2, aberto=True, cima=(0, -1, 0.3))
        velas = np.minimum(vela(g, (-7.5, -5.0, BASE), 2.2), vela(g, (7.8, -4.0, BASE), 1.6))
        bs = base(g, tipo="pedra", semente=8)
        marca = np.maximum(sigilo_sangue(g.x, g.y + 6.5, 8.5, 0.9), np.abs(g.z - BASE) - 0.25)
        bs = menos(bs, marca, 0.05)
        marca = np.maximum(marca, g.z - BASE + 0.1)
        return montar({"c1": fig, "c2": np.minimum(liv, velas), "c3": bs, "c4": marca}, ("c4", "c3", "c2"))
    return campo


if __name__ == "__main__":
    rodar_mini(__file__, "ocultista", campo_de)
