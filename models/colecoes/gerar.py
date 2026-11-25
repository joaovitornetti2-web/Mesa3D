#!/usr/bin/env python3
"""Gera uma coleção inteira: STL de foto (stl/), STL de impressão (stl_imprimir/, quando a peça tem arrumação
própria) e o 3MF de cada peça (simplificado, um objeto por cor).
Uso: python3 gerar.py <coleção> [peça ...]      (as peças e resoluções ficam em PECAS abaixo)
Cada peça roda num processo próprio com limite de memória, para não derrubar a sessão."""
import os
import resource
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
# coleção -> [(peça, passo da grade em mm, tem versão de impressão própria, arquivos 3MF extras)]
PECAS = {
    "masmorra": [("mimico", 0.3, True), ("prisao", 0.3, False), ("corujurso", 0.22, False), ("cubo", 0.3, False),
                 ("dragaozinho", 0.22, False), ("bandeja_escudo", 0.3, False), ("barril", 0.3, False),
                 ("porta_copos", 0.4, True), ("iniciativa", 0.22, True), ("porta", 0.22, False), ("contador", 0.22, True),
                 ("torre_dragao", 0.6, False)],
    "paranormal": [("caveira", 0.35, True), ("livro", 0.3, True), ("mao", 0.3, False), ("velas", 0.35, True),
                   ("gravador", 0.3, False), ("evidencias", 0.3, True), ("sanidade", 0.22, True), ("bandeja_ritual", 0.3, False),
                   ("entidade", 0.22, False), ("mascara", 0.3, False), ("olho", 0.3, False), ("torre_ritual", 0.5, False)],
}
TRES_MF_ESPECIAL = {"torre_dragao": ["torre_dragao-torre", "torre_dragao-bandeja"]}


def limite():
    resource.setrlimit(resource.RLIMIT_AS, (10_000_000_000, 10_000_000_000))


def roda(col, nome, passo, imprimir):
    args = [sys.executable, os.path.join(RAIZ, col, nome + ".py"), str(passo)] + (["--imprimir"] if imprimir else [])
    r = subprocess.run(args, capture_output=True, text=True, preexec_fn=limite)
    if r.returncode:
        print("FALHOU", nome, "imprimir" if imprimir else "foto", r.stderr[-800:], flush=True)
        return False
    print("ok", nome, "imprimir" if imprimir else "foto", flush=True)
    return True


if __name__ == "__main__":
    col = sys.argv[1]
    so = set(sys.argv[2:])
    sys.path.insert(0, RAIZ)
    from base import montar_3mf
    aqui = os.path.join(RAIZ, col, "x.py")
    for nome, passo, imp in PECAS[col]:
        if so and nome not in so:
            continue
        if not roda(col, nome, passo, False):
            continue
        if imp and not roda(col, nome, passo, True):
            continue
        for n in TRES_MF_ESPECIAL.get(nome, [nome]):
            print("  3mf", os.path.basename(montar_3mf(aqui, n, imprimir=n == nome)), flush=True)
