"""Medidor de Sanidade – mostrador antigo de pressão adaptado para a mesa: ponteiro giratório (peça separada que
encaixa num pino) marca a sanidade do personagem, de "SÃO" a "PERDIDO", com a faixa final em vermelho e uma
caveirinha no fim da escala. Aro com parafusos e pé de apoio inclinado. Ø 84 × 96 mm de altura.
Cores: c1 carcaça, c2 traços, letras e ponteiro, c3 fundo do mostrador, c4 zona vermelha.
Impressão (--imprimir): medidor deitado de costas e o ponteiro ao lado, sem suporte.
Ainda não testado: pino de 3 mm com folga 0,2 mm no furo do ponteiro (deve girar com atrito)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detalhe import *

passo, IMP = args(0.12)
R, ESP, INC = 42.0, 14.0, 12.0          # raio, espessura, inclinação para trás (graus) na foto
A0, A1 = 225.0, -45.0                    # ângulos da escala (graus, a partir do eixo x, sentido horário)
MOSTRA = 0.72                            # posição do ponteiro na foto (0 a 1)


def medidor(g):
    """medidor deitado, face para +z, centro em (0, 0); face do mostrador em z = ESP - 2."""
    X, Y, Z = g.x, g.y, g.z
    rad = np.sqrt(X ** 2 + Y ** 2)
    ang = np.degrees(np.arctan2(Y, X))
    corpo = np.maximum(rad - R, np.maximum(-Z, Z - ESP))
    corpo = smax(corpo, Z - ESP, 1.5)
    corpo = menos(corpo, np.maximum(rad - R + 5, ESP - 3.2 - Z), 0.8)                 # vidro/rebaixo do mostrador
    aro = np.maximum(np.abs(rad - R + 2.5) - 2.5, np.abs(Z - ESP - 0.4) - 1.2)
    corpo = smin(corpo, aro, 0.8)
    corpo = corpo + 0.25 * np.clip(1 - np.abs(rad - R) / 0.8, 0, 1) * (np.abs(np.mod(ang * 1.2, 3.0) - 1.5) / 1.5) * (Z > 2) * (Z < ESP - 1)   # serrilhado na lateral
    paraf = None
    for k in range(8):
        a = np.radians(k * 45 + 22.5)
        p = esfera(g, ((R - 2.5) * np.cos(a), (R - 2.5) * np.sin(a), ESP + 1.4), 1.6)
        paraf = p if paraf is None else np.minimum(paraf, p)
    zf = ESP - 3.2
    face = np.maximum(rad - R + 5, np.abs(Z - zf + 0.5) - 0.5)
    # escala: traços a cada 10 %, maiores a cada 50 %
    t = (A0 - ang) % 360 / (A0 - A1)                                    # 0..1 ao longo da escala
    tt = np.clip(t, 0, 1)
    passo_t = 0.05
    k = np.round(tt / passo_t)
    da = np.abs(tt - k * passo_t) * (A0 - A1) * np.pi / 180 * (R - 9)
    maior = (np.mod(k, 2) == 0)
    traco = np.maximum(da - np.where(maior, 0.7, 0.45), np.maximum(rad - (R - 7), np.where(maior, R - 14, R - 11) - rad))
    traco = np.maximum(traco, np.where((t > 1.02) | (t < -0.02), 10.0, 0.0))
    arco = np.maximum(np.abs(rad - (R - 7)) - 0.5, np.where((t > 1.0) | (t < 0), 10.0, -10.0))
    zona = np.maximum(np.abs(rad - (R - 9.5)) - 2.3, np.where((t > 0.78) & (t <= 1.0), -10.0, 10.0))
    marcas = np.maximum(np.minimum(traco, arco), np.abs(Z - zf - 0.3) - 0.3)
    zona = np.maximum(zona, np.abs(Z - zf - 0.25) - 0.25)
    # letras
    letras = np.minimum(texto2d(X, Y - 10, "SANIDADE", 4.6, "serif"), texto2d(X + 13, Y + 27, "SÃO", 4, "mono"))
    letras = np.minimum(letras, texto2d(X - 11, Y + 27, "PERDIDO", 3.6, "mono"))
    letras = np.maximum(letras, np.abs(Z - zf - 0.3) - 0.3)
    # caveirinha no fim da escala
    a = np.radians(A1 - 8)
    cx, cy = (R - 9.5) * np.cos(a), (R - 9.5) * np.sin(a)
    cav = smin(np.sqrt((X - cx) ** 2 + (Y - cy - 0.6) ** 2) - 3, np.maximum(np.abs(X - cx) - 1.8, np.abs(Y - cy + 2.2) - 1.4), 0.6)
    cav = menos(cav, np.minimum(np.sqrt((X - cx - 1.1) ** 2 + (Y - cy - 0.4) ** 2) - 0.8, np.sqrt((X - cx + 1.1) ** 2 + (Y - cy - 0.4) ** 2) - 0.8))
    cav = np.maximum(cav, np.abs(Z - zf - 0.4) - 0.4)
    escuro = np.minimum.reduce([marcas, letras, cav])
    pino = np.maximum(np.sqrt(X ** 2 + Y ** 2) - 1.5, np.maximum(zf - 1 - Z, Z - zf - 4.5))
    cubo = np.maximum(np.sqrt(X ** 2 + Y ** 2) - 4.2, np.maximum(zf - 1 - Z, Z - zf - 1.2))
    corpo = np.minimum.reduce([corpo, face, cubo, pino, paraf])
    tudo = np.minimum.reduce([corpo, escuro, zona])
    return tudo, escuro, face, zona


def ponteiro(g, ang, z0):
    X, Y, Z = g.x, g.y, g.z
    c, s = float(np.cos(np.radians(ang))), float(np.sin(np.radians(ang)))
    u, v = X * c + Y * s, -X * s + Y * c
    braco = np.maximum(np.maximum(-u - 7, u - (R - 12)), np.abs(v) - 1.6 * np.clip(1 - u / (R - 8), 0.25, 1))
    p = np.minimum(braco, np.sqrt(X ** 2 + Y ** 2) - 3.6)
    p = np.maximum(p, np.abs(Z - z0 - 0.8) - 0.8)
    p = menos(p, np.sqrt(X ** 2 + Y ** 2) - 1.7)                        # furo do pino
    return p


MN, MX = ((-44, -44, 0), (100, 44, ESP + 3)) if IMP else ((-46, -34, 0), (46, 30, 98))


def campo(g):
    if IMP:
        tudo, escuro, face, zona = medidor(g)
        gv = Vista(g, (0, 0, 0), np.eye(3))
        gv.x = gv.x - 62
        pont = ponteiro(gv, 90, 0.0)
    else:
        # foto: medidor em pé, inclinado para trás, sobre um pé; ponteiro montado
        C = (0, 0, 50)
        gv = Vista(g, C, mul(rot_x(90 - INC)))
        gv.z = gv.z - C[2] + ESP / 2
        gv.y = gv.y - C[1]
        tudo, escuro, face, zona = medidor(gv)
        zf = ESP - 3.2
        pont = ponteiro(gv, A0 - MOSTRA * (A0 - A1), zf + 1.6)
        pe = np.maximum(caixa(g, (0, 6, 4), (30, 16, 4), 3), -g.z)
        pe = smin(pe, caixa(Vista(g, (0, 4, 18), rot_x(-INC)), (0, 4, 18), (14, 4, 14), 3), 3)
        # Marca de Sangue gravada na frente do pé
        pe = menos(pe, np.maximum(sigilo_sangue(g.x, g.z - 4, 6, 0.9), np.abs(g.y + 10) - 0.5), 0.1)
        tudo = smin(tudo, pe, 2)
    escuro = np.minimum(escuro, pont)
    tudo = np.maximum(np.minimum(tudo, pont), -g.z)
    return tudo, {"c2": escuro, "c4": zona, "c3": face}


if __name__ == "__main__":
    for k, v in esculpir(campo, MN, MX, passo, saida(__file__, "sanidade", IMP)).items():
        print(k, v)
