#!/usr/bin/env python3
"""Gera as imagens do site (uma por combinação de cor) com render realista no Blender.

1. Exporta cada grupo de cor dos modelos OpenSCAD como STL (em site/.cache/, fora do git).
2. Renderiza cada produto no Blender (site/render_blender.py), trocando só as cores entre variantes.

Uso: python3 site/gerar_imagens.py [produto ...]     (precisa de openscad, blender e Pillow)
Saída: site/img/<produto>_<variante>.webp
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, "site")
IMG = os.path.join(SITE, "img")
CACHE = os.path.join(SITE, ".cache")
M = os.path.join(RAIZ, "models")

# cores lineares (PLA)
PRETO, BRANCO, VERMELHO, CINZA = (0.018, 0.018, 0.02), (0.78, 0.78, 0.76), (0.42, 0.008, 0.012), (0.2, 0.21, 0.22)
LARANJA, ROSA = (0.80, 0.18, 0.012), (0.85, 0.28, 0.42)


def kit(corpo):
    return f'include <{M}/kit/kit_rpg.scad>\nPARTE = "nada"; TEMA = "paranormal";\n{corpo}\n'


def caixa(e, corpo):
    return f'include <{M}/dados/caixa_elementos.scad>\nPARTE = "nada"; NOME = false; DECOR = true; ELEMENTO = "{e}";\n{corpo}\n'


def relic(e, corpo):
    return f'include <{M}/decoracao/relicario.scad>\nPARTE = "nada"; ELEMENTO = "{e}";\n{corpo}\n'


TAMPA_CX = "translate([EXT[0], 0, FUNDO + INT[2] + TAMPA_TOPO]) rotate([0, 180, 0])"
ANEIS = [0, 1, 3, 7]   # Morrendo, Sangrando, Apavorado, Enlouquecendo

# produto -> grupos (papel -> código scad), variantes (sufixo -> cor por papel), câmera
PRODUTOS = {}

PRODUTOS["torre"] = dict(
    grupos={
        "c1": kit("bandeja(); translate([TX, TY, BF]) torre(); translate([TX, TY, BF + TH]) telhado();"),
        "c2": kit("translate([TX + T / 2, TY - 0.1, BF + 70]) rotate([90, 0, 0]) brasao_base();"),
        "c3:sino": kit("translate([TX + T / 2, TY + T / 2, BF + TH + DECK_H + 7]) sino();"),
        "c3:sigilo": kit("translate([TX + T / 2, TY - 0.1, BF + 70]) rotate([90, 0, 0]) brasao_d20();"),
    },
    variantes={"preta": dict(c1=PRETO, c2=VERMELHO, c3=BRANCO), "branca": dict(c1=BRANCO, c2=VERMELHO, c3=PRETO),
               "vermelha": dict(c1=VERMELHO, c2=PRETO, c3=BRANCO)},
    cam=dict(elevacao=24, azimute=-32, tamanho=[1000, 1200], folga=1.05))

PRODUTOS["aneis"] = dict(
    grupos={
        "c1": kit(" ".join(f"translate([{(k % 2) * 40}, {-(k // 2) * 40}, 0]) anel_base();" for k, i in enumerate(ANEIS))),
        "c2": kit(" ".join(f"translate([{(k % 2) * 40}, {-(k // 2) * 40}, 0]) anel_texto({i});" for k, i in enumerate(ANEIS))),
    },
    variantes={"preto": dict(c1=PRETO, c2=BRANCO), "branco": dict(c1=BRANCO, c2=PRETO), "vermelho": dict(c1=VERMELHO, c2=BRANCO)},
    cam=dict(elevacao=52, azimute=-20, tamanho=[1200, 960], folga=1.08))

CORES_CAIXA = {"preta-vermelha": dict(c1=PRETO, c2=VERMELHO), "preta-branca": dict(c1=PRETO, c2=BRANCO),
               "branca-preta": dict(c1=BRANCO, c2=PRETO), "vermelha-preta": dict(c1=VERMELHO, c2=PRETO)}
for e in ["sangue", "morte", "conhecimento", "energia", "medo"]:   # caixa rúnica esculpida (models/dados/caixa_meshy.py)
    R = os.path.join(M, "dados", "runica")
    PRODUTOS[f"caixa_{e}"] = dict(stl={"c1": os.path.join(R, f"base_{e}_cor1.stl"), "c1:tampa": os.path.join(R, "caixa_tampa.stl"),
                                       "c2": os.path.join(R, f"base_{e}_cor2.stl")}, suave=True,
                                  variantes=CORES_CAIXA, cam=dict(elevacao=20, azimute=-24, tamanho=[1200, 1000], folga=1.02))

CORES_RELIC = {"preto-vermelho": dict(c1=PRETO, c2=VERMELHO), "preto-branco": dict(c1=PRETO, c2=BRANCO), "branco-preto": dict(c1=BRANCO, c2=PRETO)}
for e in ["sangue", "morte", "medo"]:
    PRODUTOS[f"relicario_{e}"] = dict(
        grupos={
            "c1": relic(e, "corpo(); translate([0, 0, H + 0.2]) { tampa_uso(); translate([0, 0, ZT - ASSENTO]) corte(false) medalhao(); }"),
            "c2": relic(e, "translate([0, 0, H + 0.2]) translate([0, 0, ZT - ASSENTO]) corte(true) medalhao();"),
        },
        variantes=CORES_RELIC, cam=dict(elevacao=32, azimute=-24, tamanho=[1200, 1000], folga=1.1))

# peças esculpidas no Meshy e tornadas funcionais (torre_meshy.py, bau_meshy.py)
CORES_ESC = {"preta": dict(c1=PRETO, c2=PRETO), "preta-laranja": dict(c1=PRETO, c2=LARANJA), "branca": dict(c1=BRANCO, c2=BRANCO),
             "preta-vermelha": dict(c1=PRETO, c2=VERMELHO)}
PRODUTOS["ritual"] = dict(stl={"c1": os.path.join(CACHE, "ritual_torre_montada.stl"), "c2": os.path.join(M, "torre", "ritual", "bandeja_esculpida.stl")},
                          suave=True, variantes=CORES_ESC, cam=dict(elevacao=20, azimute=-28, tamanho=[1000, 1200], folga=1.0))
PRODUTOS["bau"] = dict(stl={"c1": os.path.join(M, "kit", "bau", "bau_base.stl"), "c2": os.path.join(M, "kit", "bau", "bau_tampa.stl")},
                       suave=True, variantes={"preto": dict(c1=PRETO, c2=PRETO), "preto-laranja": dict(c1=PRETO, c2=LARANJA),
                                              "branco": dict(c1=BRANCO, c2=BRANCO), "preto-vermelho": dict(c1=PRETO, c2=VERMELHO)},
                       cam=dict(elevacao=22, azimute=-30, tamanho=[1200, 1000], folga=1.05))

# a Turma do Ateliê (models/turma): c1 corpo, c2 pupilas/boca, c3 branco dos olhos, c4 bochechas
RT = os.path.join(M, "turma", "stl")
def turma_cores(corpo, bochecha=ROSA):
    return dict(c1=corpo, c2=PRETO, c3=BRANCO, c4=bochecha)
TURMA_VAR = {"rosa": turma_cores(ROSA, VERMELHO), "laranja": turma_cores(LARANJA), "branco": turma_cores(BRANCO),
             "preto": turma_cores(PRETO), "vermelho": turma_cores(VERMELHO, ROSA)}
# a Turma esculpida (models/esculpidos): c1 corpo, c2 olhos/boca, c3 brilhos, c4 acento (chapéu, dado, gorro, flores...)
RE = os.path.join(M, "esculpidos", "stl")
def esc_cores(corpo, acento, olhos=PRETO, brilho=BRANCO):
    return dict(c1=corpo, c2=olhos, c3=brilho, c4=acento)
ESC_VAR = {"rosa": esc_cores(ROSA, VERMELHO), "laranja": esc_cores(LARANJA, VERMELHO), "branco": esc_cores(BRANCO, LARANJA),
           "preto": esc_cores(PRETO, LARANJA, BRANCO, PRETO), "vermelho": esc_cores(VERMELHO, LARANJA)}
OLHO_VAR = dict(ESC_VAR, preto=esc_cores(PRETO, VERMELHO), vermelho=esc_cores(VERMELHO, LARANJA))
CAM_ESC = {"fantasminha": (14, -24), "gosminha": (14, -24), "olhinho": (14, -18), "caveirinha": (16, -20), "morceguinho": (14, -20)}
for n, arq in [("fantasminha", "boo"), ("gosminha", "gosminha"), ("olhinho", "olhinho"), ("caveirinha", "caveirinha"), ("morceguinho", "morceguinho")]:
    el, az = CAM_ESC[n]
    PRODUTOS[f"turma_{n}"] = dict(stl={f"c{c}": os.path.join(RE, f"{arq}_c{c}.stl") for c in range(1, 5)}, suave=True,
                                  variantes=OLHO_VAR if n == "olhinho" else ESC_VAR,
                                  cam=dict(elevacao=el, azimute=az, tamanho=[1000, 1100], folga=1.02))

# brinquedos sensoriais (models/sensoriais)
RS = os.path.join(M, "sensoriais", "stl", "render")
METAL = (0.5, 0.51, 0.53)
UMA_COR = {"preto": dict(c1=PRETO), "branco": dict(c1=BRANCO), "vermelho": dict(c1=VERMELHO), "laranja": dict(c1=LARANJA), "rosa": dict(c1=ROSA)}
SENS = {
    "spinner": ({"c1": "spinner_c1", "c2": "spinner_tampa", "c3": "spinner_rol"},
                {"preto": dict(c1=PRETO, c2=VERMELHO, c3=METAL), "branco": dict(c1=BRANCO, c2=PRETO, c3=METAL),
                 "vermelho": dict(c1=VERMELHO, c2=PRETO, c3=METAL), "laranja": dict(c1=LARANJA, c2=PRETO, c3=METAL), "rosa": dict(c1=ROSA, c2=BRANCO, c3=METAL)}, 55, 1.0),
    "cone": ({"c1": "cone_c1"}, UMA_COR, 22, 1.05),
    "pedra": ({"c1": "pedra_c1", "c2": "pedra_c2", "c4": "pedra_c4"}, {k: dict(v, c2=PRETO, c4=(VERMELHO if k == "rosa" else ROSA)) for k, v in UMA_COR.items()}, 35, 1.0),
    "serpente": ({"c1": "serpente_c1", "c2": "serpente_c2", "c5": "serpente_d2", "c3": "serpente_d3", "c4": "serpente_d4"},
                 {k: dict(v, c3=BRANCO, c4=ROSA if v["c1"] != ROSA else VERMELHO, c5=PRETO if v["c1"] != PRETO else BRANCO) for k, v in
                  {"preta": dict(c1=PRETO, c2=PRETO), "rosa": dict(c1=ROSA, c2=ROSA), "preta-laranja": dict(c1=PRETO, c2=LARANJA),
                   "rosa-branca": dict(c1=ROSA, c2=BRANCO), "vermelha-preta": dict(c1=VERMELHO, c2=PRETO)}.items()}, 50, 0.95),
    "dado": ({"c1": "dado_c1"}, UMA_COR, 28, 1.05),
    "anel": ({"c1": "anel_c1", "c2": "anel_c2"},
             {"preto": dict(c1=PRETO, c2=PRETO), "preto-vermelho": dict(c1=PRETO, c2=VERMELHO), "branco-rosa": dict(c1=BRANCO, c2=ROSA),
              "preto-laranja": dict(c1=PRETO, c2=LARANJA), "rosa-branco": dict(c1=ROSA, c2=BRANCO)}, 35, 1.05),
    "piao": ({"c1": "piao_c1"}, UMA_COR, 18, 1.05),
    "d20": ({"c1": "d20_c1"}, UMA_COR, 22, 1.1),
}
for n, (partes, variantes, el, folga) in SENS.items():
    PRODUTOS[f"sens_{n}"] = dict(stl={k: os.path.join(RS, v + ".stl") for k, v in partes.items()}, suave=False,
                                 variantes=variantes, cam=dict(elevacao=el, azimute=-24, tamanho=[1200, 1000], folga=folga))

# plaquinhas (models/decor/plaquinhas.scad): c1 base, c2 relevo
RD = os.path.join(M, "decor", "stl")
CORES_PLACA = {"vermelha-branca": dict(c1=VERMELHO, c2=BRANCO), "preta-laranja": dict(c1=PRETO, c2=LARANJA),
               "rosa-branca": dict(c1=ROSA, c2=BRANCO), "branca-preta": dict(c1=BRANCO, c2=PRETO), "laranja-preta": dict(c1=LARANJA, c2=PRETO)}
for n in ["nao_perturbe", "covil", "criaturas", "bem_vindos", "home_office", "nome"]:
    PRODUTOS[f"placa_{n}"] = dict(stl={f"c{c}": os.path.join(RD, f"{n}_c{c}.stl") for c in (1, 2)}, suave=False,
                                  variantes=CORES_PLACA, cam=dict(elevacao=62, azimute=-12, tamanho=[1200, 900], folga=0.95))
# decoração (models/decor/decor.scad)
def dec(partes, variantes, el=24, folga=1.05, suave=False):
    return dict(stl={k: os.path.join(RD, f"{v}.stl") for k, v in partes.items()}, suave=suave, variantes=variantes,
                cam=dict(elevacao=el, azimute=-24, tamanho=[1000, 1100], folga=folga))
CINCO = {"preto": dict(c1=PRETO), "branco": dict(c1=BRANCO), "vermelho": dict(c1=VERMELHO), "laranja": dict(c1=LARANJA), "rosa": dict(c1=ROSA)}
ROSTO = lambda corpo, acento=ROSA: dict(c1=corpo, c2=PRETO, c3=BRANCO, c4=acento)
# decoração esculpida (models/esculpidos/decor/stl)
RDE = os.path.join(M, "esculpidos", "decor", "stl")
def dece(nome, papeis, variantes, el=20, az=-24, folga=1.05):
    return dict(stl={c: os.path.join(RDE, f"{nome}_{c}.stl") for c in papeis}, suave=True, variantes=variantes,
                cam=dict(elevacao=el, azimute=az, tamanho=[1000, 1100], folga=folga))
C4 = ("c1", "c2", "c3", "c4")
FACE = lambda corpo, acento, olhos=PRETO, brilho=BRANCO: dict(c1=corpo, c2=olhos, c3=brilho, c4=acento)
PRODUTOS["dec_lanterna"] = dece("lanterna", ("c1",), CINCO, 18, -15, 1.05)
PRODUTOS["dec_monstrinho"] = dece("monstrinho", C4, {"laranja": FACE(LARANJA, VERMELHO), "rosa": FACE(ROSA, VERMELHO), "vermelho": FACE(VERMELHO, ROSA),
                                                     "preto": FACE(PRETO, LARANJA), "branco": FACE(BRANCO, ROSA)}, 16, -24)
PRODUTOS["dec_porta_chaves"] = dece("porta_chaves", ("c1", "c2"), {"preto-laranja": dict(c1=PRETO, c2=LARANJA), "preto-vermelho": dict(c1=PRETO, c2=VERMELHO),
                                                                  "branco-preto": dict(c1=BRANCO, c2=PRETO), "rosa-branco": dict(c1=ROSA, c2=BRANCO)}, 40, -25, 1.0)
PRODUTOS["dec_vaso"] = dece("vaso", ("c1",), CINCO, 16, -20)
PRODUTOS["dec_porta_copos"] = dece("porta_copos", ("c1", "c2"), {"branco-preto": dict(c1=BRANCO, c2=PRETO), "rosa-branco": dict(c1=ROSA, c2=BRANCO),
                                                                "laranja-branco": dict(c1=LARANJA, c2=BRANCO), "preto-rosa": dict(c1=PRETO, c2=ROSA)}, 42, -20, 1.0)
PRODUTOS["dec_gatinho"] = dece("gatinho", C4, {"laranja": FACE(LARANJA, VERMELHO), "rosa": FACE(ROSA, VERMELHO), "branco": FACE(BRANCO, LARANJA),
                                               "preto": FACE(PRETO, LARANJA, BRANCO, PRETO)}, 26, -40)

# miniaturas e brinquedinhos do Meshy (STL já preparado em models/kit/meshy_op/<nome>_pronto.stl)
CORES_MINI = {"branco": dict(c1=BRANCO), "preto": dict(c1=PRETO), "vermelho": dict(c1=VERMELHO)}
CORES_CHIBI = {"branco": dict(c1=BRANCO), "preto": dict(c1=PRETO), "rosa": dict(c1=ROSA), "laranja": dict(c1=LARANJA)}
for n in ["ocultista", "combatente", "especialista", "criatura", "sombra", "chibi_agente", "chibi_criatura"]:
    PRODUTOS[f"mini_{n}"] = dict(stl={"c1": os.path.join(M, "kit", "meshy_op", f"{n}_pronto.stl")}, suave=True,
                                 variantes=CORES_CHIBI if n.startswith("chibi") else CORES_MINI, cam=dict(elevacao=14, azimute=-22, tamanho=[1000, 1200], folga=1.02))


def exportar(args):
    nome, papel, scad = args
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"{nome}_{papel.replace(':', '_')}.scad")
    stl = os.path.join(CACHE, f"{nome}_{papel.replace(':', '_')}.stl")
    if os.path.exists(stl) and os.path.exists(f) and open(f).read() == scad:
        return stl
    open(f, "w").write(scad)
    subprocess.run(["openscad", "-q", "-o", stl, f], check=True, cwd=CACHE)
    return stl


def renderizar(nome):
    p = PRODUTOS[nome]
    partes = [{"stl": s, "papel": k.split(":")[0], "suave": p.get("suave", False)} for k, s in p["stls"].items()]
    pngs = {os.path.join(CACHE, f"{nome}_{v}.png"): cores for v, cores in p["variantes"].items()}
    trab = os.path.join(CACHE, f"{nome}.json")
    json.dump({"partes": partes, "variantes": pngs, "amostras": 72, "estudio": p.get("estudio", "vivo"), **p["cam"]}, open(trab, "w"))
    r = subprocess.run(["blender", "-b", "-noaudio", "-P", os.path.join(SITE, "render_blender.py"), "--", trab],
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(nome + "\n" + r.stdout[-2000:] + r.stderr[-2000:])
    for png, _ in pngs.items():
        im = Image.open(png).convert("RGB")
        im.thumbnail((1000, 1000))
        im.save(os.path.join(IMG, os.path.basename(png)[:-4] + ".webp"), quality=84)
    return nome


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    nomes = sys.argv[1:] or list(PRODUTOS)
    trabalhos = [(n, papel, scad) for n in nomes for papel, scad in PRODUTOS[n].get("grupos", {}).items()]
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        stls = list(ex.map(exportar, trabalhos))
    for (n, papel, _), stl in zip(trabalhos, stls):
        PRODUTOS[n].setdefault("stls", {})[papel] = stl
    for n in nomes:
        PRODUTOS[n].setdefault("stls", PRODUTOS[n].get("stl", {}))
        if all(os.path.exists(s) for s in PRODUTOS[n]["stls"].values()):
            print("ok", renderizar(n), flush=True)
        else:
            print("sem STL, pulei:", n, flush=True)
