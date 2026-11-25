"""Atalhos comuns das coleções: importa a biblioteca SDF das peças esculpidas e padroniza saída e 3MF."""
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(RAIZ), "esculpidos"))
from sdf import *  # noqa: F401,F403
import numpy as np  # noqa: F401


def args(padrao=0.3):
    """passo da grade (1º argumento) e se é a versão de impressão (--imprimir)."""
    nums = [a for a in sys.argv[1:] if not a.startswith("--")]
    return (float(nums[0]) if nums else padrao), ("--imprimir" in sys.argv)


def saida(arquivo, nome, imprimir=False):
    """caminho base dos STL: <coleção>/stl/<nome> (foto) ou <coleção>/stl_imprimir/<nome>."""
    pasta = os.path.join(os.path.dirname(os.path.abspath(arquivo)), "stl_imprimir" if imprimir else "stl")
    return os.path.join(pasta, nome)


def montar_3mf(arquivo, nome, imprimir=True):
    """junta os STL de cada cor num 3MF (um objeto por cor, para escolher o filamento no Bambu Studio)."""
    import trimesh
    base = saida(arquivo, nome, imprimir)
    if not os.path.exists(base + "_c1.stl"):
        base = saida(arquivo, nome, False)
    s = trimesh.Scene()
    for c in ["c1", "c2", "c3", "c4", "c5"]:
        f = f"{base}_{c}.stl"
        if os.path.exists(f):
            s.add_geometry(trimesh.load(f), node_name=f"{nome}_{c}", geom_name=f"{nome}_{c}")
    out = os.path.join(os.path.dirname(os.path.abspath(arquivo)), f"{nome}.3mf")
    open(out, "wb").write(trimesh.exchange.threemf.export_3MF(s))
    return out
