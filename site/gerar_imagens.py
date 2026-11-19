#!/usr/bin/env python3
"""Gera as imagens do site (uma por combinação de cor) a partir dos modelos OpenSCAD.

Uso: python3 site/gerar_imagens.py      (precisa de openscad, xvfb-run e Pillow)
Saída: site/img/<produto>_<variante>.webp
"""
import itertools
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageChops

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "site", "img")
M = os.path.join(RAIZ, "models")

PRETO, BRANCO, VERMELHO = "#1a1a1a", "#f2f2f2", "#c0141c"

# id da cor -> [cor principal, cor de destaque, cor de detalhe]
CORES_TORRE = {"preta": [PRETO, VERMELHO, BRANCO], "branca": [BRANCO, VERMELHO, PRETO], "vermelha": [VERMELHO, PRETO, BRANCO]}
CORES_ANEIS = {"preto": [PRETO, BRANCO], "branco": [BRANCO, PRETO], "vermelho": [VERMELHO, BRANCO]}
CORES_CAIXA = {"preta-vermelha": [PRETO, VERMELHO], "preta-branca": [PRETO, BRANCO], "branca-preta": [BRANCO, PRETO], "vermelha-preta": [VERMELHO, PRETO]}
EMBLEMAS = {"gota": "sangue", "ampulheta": "morte", "olho": "conhecimento", "raio": "energia", "estrela": "medo"}
CORES_RELIC = {"preto-vermelho": [PRETO, VERMELHO], "preto-branco": [PRETO, BRANCO], "branco-preto": [BRANCO, PRETO]}
SELOS = {"gota": "sangue", "espiral": "morte", "estrela": "medo"}


def torre(c):
    return f"""include <{M}/kit/kit_rpg.scad>
PARTE = "nada";
color("{c[0]}") bandeja();
color("{c[0]}") translate([TX, TY, BF]) torre();
color("{c[0]}") translate([TX, TY, BF + TH]) telhado();
color("{c[2]}") translate([TX + T / 2, TY + T / 2, BF + TH + DECK_H + 7]) sino();
translate([TX + T / 2, TY - 0.1, BF + 70]) rotate([90, 0, 0]) {{ color("{c[1]}") brasao_base(); color("{c[2]}") brasao_d20(); }}
""", "--camera=0,0,0,60,0,35,0", "1200,1200"


def aneis(c):
    return f"""include <{M}/kit/kit_rpg.scad>
PARTE = "nada";
for (i = [0:3]) translate([(i % 2) * 34, -floor(i / 2) * 34, 0]) {{ color("{c[0]}") anel_base(); color("{c[1]}") anel_texto(i); }}
""", "--camera=0,0,0,40,0,20,0", "1400,1400"


def caixa(e, c):
    return f"""include <{M}/dados/caixa_elementos.scad>
PARTE = "nada"; NOME = false; ELEMENTO = "{e}";
color("{c[0]}") caixa();
translate([EXT[0], 0, FUNDO + INT[2] + TAMPA_TOPO]) rotate([0, 180, 0]) {{
  color("{c[0]}") difference() {{ tampa_corpo(); translate([0, 0, -0.01]) linear_extrude(INLAY + 0.01) arte_impressao(ELEMENTO); }}
  color("{c[1]}") translate([0, 0, -0.02]) linear_extrude(INLAY + 0.02) arte_impressao(ELEMENTO);
}}
""", "--camera=44,29,14,55,0,20,250", "1200,900"


def relicario(e, c):
    return f"""include <{M}/decoracao/relicario.scad>
PARTE = "nada"; ELEMENTO = "{e}";
color("{c[0]}") corpo();
translate([0, 0, H + 0.2]) {{
  color("{c[0]}") tampa_uso();
  translate([0, 0, ZT - ASSENTO]) {{ color("{c[0]}") corte(false) medalhao(); color("{c[1]}") corte(true) medalhao(); }}
}}
""", "--camera=0,0,0,55,0,25,0", "1200,1000"


def trabalhos():
    for k, c in CORES_TORRE.items():
        yield f"torre_{k}", torre(c)
    for k, c in CORES_ANEIS.items():
        yield f"aneis_{k}", aneis(c)
    for (ek, e), (k, c) in itertools.product(EMBLEMAS.items(), CORES_CAIXA.items()):
        yield f"caixa_{ek}_{k}", caixa(e, c)
    for (sk, e), (k, c) in itertools.product(SELOS.items(), CORES_RELIC.items()):
        yield f"relicario_{sk}_{k}", relicario(e, c)


def render(item):
    nome, (scad, camera, tam) = item
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "v.scad")
        png = os.path.join(tmp, "v.png")
        open(f, "w").write(scad)
        args = ["xvfb-run", "-a", "openscad", "-q", "-o", png, f"--imgsize={tam}", "--colorscheme=Tomorrow", camera]
        if "--camera=0,0,0" in camera:
            args += ["--autocenter", "--viewall"]
        subprocess.run(args + [f], check=True, cwd=tmp, capture_output=True)
        im = Image.open(png).convert("RGB")
    fundo = Image.new("RGB", im.size, im.getpixel((0, 0)))
    b = ImageChops.difference(im, fundo).getbbox()
    p = 40
    im = im.crop((max(0, b[0] - p), max(0, b[1] - p), min(im.width, b[2] + p), min(im.height, b[3] + p)))
    im.thumbnail((1000, 1000))
    im.save(os.path.join(IMG, nome + ".webp"), quality=82)
    return nome


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        for n in ex.map(render, list(trabalhos())):
            print("ok", n)
