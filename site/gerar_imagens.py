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
CORES_ESC = {"preta": dict(c1=PRETO, c2=PRETO), "cinza": dict(c1=CINZA, c2=CINZA), "branca": dict(c1=BRANCO, c2=BRANCO),
             "preta-vermelha": dict(c1=PRETO, c2=VERMELHO)}
PRODUTOS["ritual"] = dict(stl={"c1": os.path.join(CACHE, "ritual_torre_montada.stl"), "c2": os.path.join(M, "torre", "ritual", "bandeja_esculpida.stl")},
                          suave=True, variantes=CORES_ESC, cam=dict(elevacao=20, azimute=-28, tamanho=[1000, 1200], folga=1.0))
PRODUTOS["bau"] = dict(stl={"c1": os.path.join(M, "kit", "bau", "bau_base.stl"), "c2": os.path.join(M, "kit", "bau", "bau_tampa.stl")},
                       suave=True, variantes={"preto": dict(c1=PRETO, c2=PRETO), "cinza": dict(c1=CINZA, c2=CINZA),
                                              "branco": dict(c1=BRANCO, c2=BRANCO), "preto-vermelho": dict(c1=PRETO, c2=VERMELHO)},
                       cam=dict(elevacao=22, azimute=-30, tamanho=[1200, 1000], folga=1.05))

# miniaturas e brinquedinhos do Meshy (STL já preparado em models/kit/meshy_op/<nome>_pronto.stl)
CORES_MINI = {"cinza": dict(c1=CINZA), "branco": dict(c1=BRANCO), "preto": dict(c1=PRETO)}
for n in ["ocultista", "combatente", "especialista", "criatura", "chibi_agente", "chibi_criatura"]:
    PRODUTOS[f"mini_{n}"] = dict(stl={"c1": os.path.join(M, "kit", "meshy_op", f"{n}_pronto.stl")}, suave=True,
                                 variantes=CORES_MINI, cam=dict(elevacao=14, azimute=-22, tamanho=[1000, 1200], folga=1.02))


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
    json.dump({"partes": partes, "variantes": pngs, "amostras": 72, "estudio": "creme", **p["cam"]}, open(trab, "w"))
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
