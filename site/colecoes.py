#!/usr/bin/env python3
"""Coleções temáticas do site (models/colecoes): fonte única para fotos, preços e o trecho do site.

Uso:
  python3 site/colecoes.py precos            mostra gramas, horas e preço de cada peça
  python3 site/colecoes.py imagens [id ...]  renderiza as fotos (site/img/col_<id>_<cor>.webp)
  python3 site/colecoes.py site              escreve as seções e os produtos no site/index.html (entre marcadores)

Nome e descrição vêm da docstring de cada script (texto antes de "Cores:", sem notas técnicas de impressão).
Preço: mesma conta de site/precos.py (filamento + máquina, × 3, termina em 9,90), com o peso estimado pelas malhas
de impressão e as horas pelo peso; peças multicolor somam purga e tempo de troca de cor."""
import ast
import json
import math
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, "site")
COL = os.path.join(RAIZ, "models", "colecoes")
IMG = os.path.join(SITE, "img")
CACHE = os.path.join(SITE, ".cache")

COLECOES = [
    ("masmorra", "Dungeons & Dragons", "Peças da mesa de D&D", "Dragões, mímicos e cubos de gosma: a masmorra inteira na sua mesa"),
    ("paranormal", "Ordem Paranormal", "Para os agentes da Ordo Realitas", "Para a mesa de quem investiga o que não devia existir"),
    ("tempestade", "Tormenta 20", "Aventuras em Arton", "Minotauros, goblins inventores e a tempestade rubra no horizonte"),
    ("bicicleta", "Kids on Bikes", "Aventura anos 80 de Kids on Bikes", "Walkie-talkie na mão, fita no bolso e a turma de bicicleta atrás do mistério"),
]
ORDEM = {
    "masmorra": ["torre_dragao", "mimico", "prisao", "cubo", "dragaozinho", "corujurso", "bandeja_escudo", "contador", "iniciativa", "porta", "barril", "porta_copos"],
    "paranormal": ["torre_ritual", "livro", "caveira", "evidencias", "sanidade", "bandeja_ritual", "entidade", "olho", "velas", "mao", "gravador", "mascara"],
    "tempestade": ["torre_tempestade", "minotauro", "goblin", "aberracao", "bau", "elmo", "moedas", "bandeja_nuvem", "pergaminho", "gargula", "arvore", "machado"],
    "bicicleta": ["fliperama", "walkie", "fita", "boombox", "bmx", "casa_arvore", "barra_vida", "disquete", "mochila", "lanterna", "placa_clube", "chaveiro_fita"],
}
# ajustes por peça: unidade do preço, divisor/multiplicador do peso (conjuntos), malhas para o peso, câmera
NOMES = {   # nomes oficiais dos sistemas (sobrepõem o nome do docstring)
    "corujurso": "Urso-Coruja", "dragaozinho": "Dragãozinho do 20 Natural", "bandeja_escudo": "Bandeja Escudo do Mestre",
    "torre_ritual": "Torre da Ordo Realitas", "livro": "Livro do Outro Lado", "sanidade": "Medidor de Sanidade",
    "evidencias": "Caixa de Evidências da Ordo Realitas", "entidade": "Criatura do Outro Lado", "bandeja_ritual": "Bandeja Círculo de Ritual",
    "torre_tempestade": "Torre da Tormenta", "minotauro": "Minotauro de Tapista", "aberracao": "Lefeu da Tormenta",
    "bandeja_nuvem": "Bandeja da Tormenta", "moedas": "Tibares de Arton", "pergaminho": "Pergaminho de Arton",
    "machado": "Machado de Tapista", "arvore": "Árvore de Arton",
}
AJUSTES = {
    "iniciativa": dict(unidade="conjunto de 8"),
    "moedas": dict(unidade="conjunto de 30", mult=10),
    "porta_copos": dict(unidade="4 porta-copos e suporte", malhas="stl"),
    "disquete": dict(unidade="4 porta-copos e estojo", malhas="stl"),
    "chaveiro_fita": dict(unidade="cada", mult=0.25),
    "torre_dragao": dict(unidade="torre e bandeja", malhas=["torre_dragao-torre", "torre_dragao-bandeja"]),
    "torre_ritual": dict(unidade="torre com bandeja"),
    "torre_tempestade": dict(unidade="torre com bandeja"),
    "fliperama": dict(unidade="torre com bandeja"),
    "contador": dict(unidade="suporte, 2 rodas e pino"),
    "barra_vida": dict(unidade="régua e 10 corações"),
    "velas": dict(unidade="prato e 3 velas (velinhas de LED não inclusas)"),
    "olho": dict(unidade="a peça (vela de LED não inclusa)"),
}
CAM = {   # elevação, azimute, folga
    "torre_dragao": (18, -26, 1.0), "torre_ritual": (18, -26, 1.0), "torre_tempestade": (18, -26, 1.0), "fliperama": (16, -28, 1.0),
    "bandeja_escudo": (55, -12, 0.95), "bandeja_ritual": (55, -15, 0.95), "bandeja_nuvem": (52, -15, 0.95), "placa_clube": (60, -10, 0.95),
    "mascara": (60, -10, 1.0), "moedas": (40, -15, 1.0), "chaveiro_fita": (50, -15, 1.0), "barra_vida": (45, -12, 0.95),
    "contador": (18, -22, 1.05), "sanidade": (10, -20, 1.0), "mao": (14, -40, 1.0), "bmx": (14, -20, 1.0), "livro": (38, -28, 1.0),
    "fita": (45, -20, 1.0), "disquete": (28, -22, 1.0), "porta_copos": (30, -25, 1.0), "iniciativa": (14, -18, 1.0),
    "pergaminho": (26, -25, 1.0), "bau": (24, -28, 1.0), "mimico": (26, -24, 1.0),
}
# cores lineares (PLA) para o render e hexadecimais para as bolinhas do site
LIN = {"preto": (0.018, 0.018, 0.02), "branco": (0.78, 0.78, 0.76), "vermelho": (0.42, 0.008, 0.012),
       "laranja": (0.80, 0.18, 0.012), "rosa": (0.85, 0.28, 0.42)}
HEX = {"preto": "#1a1a1a", "branco": "#ece9e2", "vermelho": "#c0141c", "laranja": "#f26b1d", "rosa": "#f28bb0"}
NOME_COR = {"preto": "Preto", "branco": "Branco", "vermelho": "Vermelho", "laranja": "Laranja"}


def papeis(corpo):
    """cor de cada papel para um corpo: c2 escuro/metal, c3 claro, c4 destaque, c5 chama/extra (sempre contrastando)."""
    return {"c1": corpo,
            "c2": "branco" if corpo == "preto" else "preto",
            "c3": "branco",                       # dentes, olhos, ossos, etiquetas: sempre brancos
            "c4": "laranja" if corpo == "vermelho" else "vermelho",
            "c5": "vermelho" if corpo == "laranja" else "laranja"}


VARIANTES = ["preto", "vermelho", "branco", "laranja"]


def docstring(col, n):
    return ast.get_docstring(ast.parse(open(os.path.join(COL, col, n + ".py"), encoding="utf-8").read())) or ""


def texto_cliente(doc):
    corpo = doc.split("Cores:")[0]
    nome, _, desc = corpo.partition(" – ")
    desc = " ".join(desc.split())
    desc = re.sub(r"\s*\([^)]*(SRD|folga|suporte|imprime)[^)]*\)", "", desc)
    frases = re.split(r"(?<=[.!?])\s+", desc)
    ruins = ("folga", "Impressão", "sem suporte", "suporte em árvore", "Ainda não testado", "Foto:", "fatiador", "Uma peça só")
    frases = [f.strip() for f in frases if f and not any(r.lower() in f.lower() for r in ruins)]
    d = " ".join(frases).strip()
    d = d[0].upper() + d[1:] if d else d
    return nome.strip(), d


def stls(col, n, pasta="stl"):
    d = os.path.join(COL, col, pasta)
    return [os.path.join(d, f"{n}_{c}.stl") for c in ["c1", "c2", "c3", "c4", "c5"] if os.path.exists(os.path.join(d, f"{n}_{c}.stl"))]


def malhas_peso(col, n):
    aj = AJUSTES.get(n, {})
    m = aj.get("malhas")
    if isinstance(m, list):
        return sum((stls(col, k) for k in m), [])
    if m == "stl":
        return stls(col, n)
    return stls(col, n, "stl_imprimir") or stls(col, n)


def gramas_horas(col, n):
    sys.path.insert(0, SITE)
    import importlib
    precos = importlib.import_module("precos")
    ms = malhas_peso(col, n)
    cores = len({os.path.basename(m).split("_")[-1] for m in ms})
    g = precos.gramas(ms, 1) * AJUSTES.get(n, {}).get("mult", 1)
    purga = 6.0 * (cores - 1)
    horas = g / (14 + min(g, 150) / 15) + 0.35 * (cores - 1) + 0.2   # peça grande imprime mais rápido por grama
    return g + purga, horas, cores


def preco(g, horas):
    custo = g * 149.0 / 1000 + horas * 1.50
    return max(19.90, math.ceil((custo * 3 + 0.1) / 10) * 10 - 0.10)


def medidas(col, n):
    import trimesh
    ms = [trimesh.load(f) for f in stls(col, n)]
    mn = min(m.bounds[0][0] for m in ms), min(m.bounds[0][1] for m in ms), min(m.bounds[0][2] for m in ms)
    mx = max(m.bounds[1][0] for m in ms), max(m.bounds[1][1] for m in ms), max(m.bounds[1][2] for m in ms)
    return [round(mx[i] - mn[i]) for i in range(3)]


def pecas():
    for col, *_ in COLECOES:
        for n in ORDEM[col]:
            yield col, n


def cmd_precos():
    print(f"{'peça':<28}{'g':>6}{'h':>6}{'cores':>6}{'preço':>9}")
    for col, n in pecas():
        g, h, c = gramas_horas(col, n)
        print(f"{col + '/' + n:<28}{g:>6.0f}{h:>6.1f}{c:>6}{preco(g, h):>9.2f}")


def leve(stl, alvo=1_200_000):
    """cópia simplificada do STL para a foto (o detalhe fino continua visível; o Blender fica leve)."""
    import trimesh, fast_simplification
    out = os.path.join(CACHE, "leve", os.path.basename(stl))
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(stl):
        return out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    m = trimesh.load(stl)
    if len(m.faces) > alvo:
        v, f = fast_simplification.simplify(m.vertices.astype("float32"), m.faces, 1 - alvo / len(m.faces))
        m = trimesh.Trimesh(v, f, process=True)
    m.export(out)
    return out


def cmd_imagens(so):
    from PIL import Image
    os.makedirs(CACHE, exist_ok=True)
    for col, n in pecas():
        if so and n not in so:
            continue
        partes = [{"stl": leve(s), "papel": os.path.basename(s)[:-4].split("_")[-1], "suave": True} for s in stls(col, n)]
        usados = {p["papel"] for p in partes}
        pngs = {os.path.join(CACHE, f"col_{n}_{v}.png"): {k: LIN[c] for k, c in papeis(v).items() if k in usados} for v in VARIANTES}
        el, az, folga = CAM.get(n, (18, -26, 1.02))
        trab = os.path.join(CACHE, f"col_{n}.json")
        json.dump({"partes": partes, "variantes": pngs, "amostras": 56, "estudio": "vivo", "elevacao": el, "azimute": az,
                   "folga": folga, "tamanho": [1000, 1100]}, open(trab, "w"))
        r = subprocess.run(["blender", "-b", "-noaudio", "-P", os.path.join(SITE, "render_blender.py"), "--", trab], capture_output=True, text=True)
        if r.returncode:
            print("FALHOU", n, r.stderr[-500:], flush=True)
            continue
        for png in pngs:
            im = Image.open(png).convert("RGB")
            im.thumbnail((1000, 1000))
            im.save(os.path.join(IMG, os.path.basename(png)[:-4] + ".webp"), quality=84)
        print("ok", n, flush=True)


def cmd_site():
    prods, grupos = [], []
    for col, titulo, sobre, chamada in COLECOES:
        grupos.append({"id": col, "nome": titulo, "cats": [f"col-{col}"], "desc": f"{sobre}. {chamada}."})
        for n in ORDEM[col]:
            nome, desc = texto_cliente(docstring(col, n))
            nome = NOMES.get(n, nome)
            g, h, cores = gramas_horas(col, n)
            x, y, z = medidas(col, n)
            usados = {os.path.basename(s)[:-4].split("_")[-1] for s in stls(col, n)}
            itens = []
            for v in VARIANTES:
                p = papeis(v)
                destaque = p["c4"] if "c4" in usados else (p["c2"] if "c2" in usados else None)
                cor = [HEX[v]] + ([HEX[destaque]] if destaque and destaque != v else [])
                itens.append({"id": v, "nome": NOME_COR[v] + (f" com {NOME_COR.get(destaque, destaque).lower()}" if destaque and destaque != v else ""), "cor": cor})
            prods.append({
                "id": f"{col}-{n}", "categoria": f"col-{col}", "nome": nome, "selo": "Coleção nova",
                "unidade": AJUSTES.get(n, {}).get("unidade", "a peça"), "desc": desc,
                "medidas": [["Tamanho", f"{x} × {y} × {z} mm"], ["Cores", f"{cores} {'cor' if cores == 1 else 'cores'} no AMS"]],
                "opcoes": [{"chave": "cor", "nome": "Cor", "itens": itens}],
                "_img": f"img/col_{n}_", "preco": round(preco(g, h), 2),
            })
    js = "const COLECOES = [\n" + ",\n".join(json.dumps(p, ensure_ascii=False) for p in prods) + "\n];\n"
    js += "COLECOES.forEach(p => { const base = p._img; p.img = s => base + s.cor + \".webp\"; p.alt = s => p.nome + \" na cor \" + s.nomes.cor.toLowerCase(); PRODUTOS.push(p); });\n"
    js += "GRUPOS.push(" + ", ".join(json.dumps(g, ensure_ascii=False) for g in grupos) + ");\n"
    f = os.path.join(SITE, "index.html")
    s = open(f, encoding="utf-8").read()

    def troca(s, ini, fim, novo):
        if ini in s:
            a, b = s.index(ini) + len(ini), s.index(fim)
            return s[:a] + "\n" + novo + s[b:]
        raise SystemExit("marcador não encontrado: " + ini)
    s = troca(s, "// COLECOES-JS", "// /COLECOES-JS", js)
    open(f, "w", encoding="utf-8").write(s)
    print("ok", len(prods), "produtos")


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "precos"
    {"precos": cmd_precos, "site": cmd_site}.get(acao, lambda: cmd_imagens(set(sys.argv[2:])))()
